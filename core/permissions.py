from rest_framework import permissions
from django.db.models import Q

# We'll import your models so we can discover the .use_case attribute, etc.
from usecases.models import UseCase

class IsOrgMemberOrOwner(permissions.BasePermission):
    """
    A generic permission that ensures the requesting user is either:
      1) a member of the Organization that owns the related UseCase, or
      2) the 'owner' field on that UseCase, or
      3) a superuser.

    For object-level checks, we detect the use_case (or org_id) from `obj`.
    You may extend this logic if your model references are different.
    """

    def has_permission(self, request, view):
        # Must be authenticated at minimum
        if not request.user or not request.user.is_authenticated:
            return False
        return True  # We'll do deeper checks in has_object_permission.

    def has_object_permission(self, request, view, obj):
        # Superuser override
        if request.user.is_superuser:
            return True

        # Attempt to locate the use_case or organization ID from the object.
        # (We check a few possibilities below.)

        # If obj *is* a UseCase:
        if hasattr(obj, "organization_id") and hasattr(obj, "owner"):
            org_id = obj.organization_id
            owner_user = obj.owner

        # If obj has a .use_case (e.g. WorkflowInstance, DSLDefinition, Feedback)
        elif hasattr(obj, "use_case") and obj.use_case is not None:
            org_id = obj.use_case.organization_id
            owner_user = obj.use_case.owner

        # If obj is a Feedback that references a workflow or workflow_task, etc.:
        # (You could add extra fallback logic, e.g. if `obj.workflow_task.workflow.use_case`)
        elif hasattr(obj, "workflow") and obj.workflow is not None:
            org_id = obj.workflow.use_case.organization_id
            owner_user = obj.workflow.use_case.owner

        else:
            # If we can't figure out the organization or use_case, deny by default
            return False

        # Check if the requesting user is the use_case owner
        if owner_user == request.user:
            return True

        # Check if the requesting user is a member of that organization
        user_org_ids = request.user.team_memberships.values_list(
            "team__organization_id", flat=True
        ).distinct()

        return (org_id in user_org_ids)
    