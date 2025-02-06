from rest_framework import permissions


class IsUserOrSuperuserOrCreate(permissions.BasePermission):
    """
    Permission that allows:
      - Anyone to create a user (signup).
      - Superusers to list and view any user.
      - A user to view/update their own user object.
      - Denies access otherwise.
    """

    def has_permission(self, request, view):
        # Allow creating new user accounts
        if view.action == 'create':
            return True

        # Must be authenticated for other actions
        if not request.user or not request.user.is_authenticated:
            return False

        # If it's a "list" action, only superusers may proceed
        if view.action == 'list':
            return request.user.is_superuser

        # Otherwise pass down to has_object_permission for retrieve, update, etc.
        return True

    def has_object_permission(self, request, view, obj):
        """
        Object-level checks (retrieve, update, partial_update, destroy):
        - Superusers can do anything.
        - The user can act on their own object.
        """
        if request.user.is_superuser:
            return True
        return obj == request.user
