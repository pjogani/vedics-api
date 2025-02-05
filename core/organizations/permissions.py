from rest_framework import permissions
from .models import Organization, Team, TeamMembership

class IsOrganizationOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission that allows only organization owners (or superusers) to modify.
    Read-only for others.
    """

    def has_object_permission(self, request, view, obj):
        # obj will be an Organization instance
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            return obj.owners.filter(pk=request.user.pk).exists()
        return False


class IsTeamAdminOrReadOnly(permissions.BasePermission):
    """
    Permission that grants write access if the user is:
    - superuser, or
    - an owner of the parent organization, or
    - a member of the team with role=admin
    Otherwise, read-only is allowed.
    """
    def has_object_permission(self, request, view, obj):
        # obj might be Team or TeamMembership
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.is_superuser:
            return True

        if isinstance(obj, Team):
            # Check if user is an owner of org
            org = obj.organization
            if org.owners.filter(pk=user.pk).exists():
                return True
            # Or admin membership
            return TeamMembership.objects.filter(team=obj, user=user, role='admin').exists()

        if isinstance(obj, TeamMembership):
            # For membership objects, check the team
            team = obj.team
            org = team.organization
            if org.owners.filter(pk=user.pk).exists():
                return True
            return TeamMembership.objects.filter(team=team, user=user, role='admin').exists()

        return False
