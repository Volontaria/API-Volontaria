from rest_framework import permissions
from rest_framework.permissions import DjangoModelPermissions

from .models import Event


class EventIsManager(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        is_manager = request.user in obj.cell.managers.all()

        return is_manager or request.user.is_superuser


class ParticipationIsManager(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    @staticmethod
    def if_cell_manager_or_admin(request, view, obj):
        dj_perm = DjangoModelPermissions()

        if obj:
            is_manager = request.user in obj.event.cell.managers.all()

            is_django_perms = dj_perm.has_object_permission(
                request, view, obj
            )

        else:
            is_manager = False

            # Need to get the event of the request to validates permissions
            event_id = request.data.get('event', None)

            if event_id:
                event = Event.objects.filter(pk=event_id).first()
                if event:
                    is_manager = request.user in event.cell.managers.all()

            is_django_perms = dj_perm.has_permission(
                request, view
            )

        return (is_manager and is_django_perms) or request.user.is_superuser


    @staticmethod
    def if_can_do_actions(request, view, obj):
        is_admin = ParticipationIsManager.if_cell_manager_or_admin(request, view, obj)

        is_owner = False
        if obj:
            is_owner = obj.user == request.user

        return is_owner or is_admin

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object
        # or to a Cell Manager.
        can_edit = self.if_can_do_actions(request, view, obj)

        return can_edit
