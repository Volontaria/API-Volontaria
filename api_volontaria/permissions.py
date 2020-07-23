from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow admins or owners of an object to view/edit.
    """

    def has_object_permission(self, request, view, obj):
        # Test if the object is the user himself otherwise verifies
        # if a owner field exists and equals the user.
        return (request.user.is_staff or
                obj == request.user or
                (hasattr(obj, 'owner') and obj.owner == request.user))


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins or owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Test if the object is the user himself otherwise verifies
        # if a owner field exists and equals the user.
        return (request.user.is_staff or
                obj == request.user or
                (hasattr(obj, 'owner') and obj.owner == request.user))


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to modify objects.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff
