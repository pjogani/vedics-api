from rest_framework import permissions
from django.db.models import Q
from core.organizations.models import Organization

class ProfilePermission(permissions.BasePermission):
    """
    Custom permission for UserProfile objects:
      1) Superusers can do any action on any profile.
      2) The profile's own user can view or update their profile.
      3) If the profile has allow_org_access=True, other users in the
         same organization can view (SAFE_METHODS).
      4) If the profile has allow_org_access=True AND the requesting user
         is an org owner of a shared org with that profile user, then they
         can also update the profile (non-safe methods).
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        # 1) Superuser can do anything
        if user.is_superuser:
            return True

        # 2) Owner can do anything on their own profile
        if obj.user == user:
            return True

        # 3) Must have allow_org_access to share with org members
        if not obj.allow_org_access:
            return False

        # Check if user shares at least one organization with the profile's user
        user_org_ids = set(user.team_memberships.values_list("team__organization_id", flat=True))
        owner_org_ids = set(obj.user.team_memberships.values_list("team__organization_id", flat=True))
        shared_orgs = user_org_ids.intersection(owner_org_ids)
        if not shared_orgs:
            return False

        # If it's a read-only request (GET, HEAD, OPTIONS), allow it
        if request.method in permissions.SAFE_METHODS:
            return True

        # For updates/deletes, must also be an owner in at least one shared org
        # We'll see if the user is an org owner in one of those shared orgs
        # i.e. the user appears in Organization.owners for that org
        orgs_where_user_is_owner = Organization.objects.filter(pk__in=shared_orgs, owners=user)
        return orgs_where_user_is_owner.exists()
