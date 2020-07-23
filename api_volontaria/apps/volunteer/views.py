from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions, \
    DRYPermissionFiltersBase
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from api_volontaria.apps.volunteer.models import (
    Cell,
    Event,
    TaskType,
    Participation,
)
from api_volontaria.apps.volunteer.serializers import (
    CellSerializer,
    EventSerializer,
    TaskTypeSerializer,
    ParticipationSerializer,
)


class CellViewSet(viewsets.ModelViewSet):

    serializer_class = CellSerializer
    queryset = Cell.objects.all()
    filter_fields = '__all__'
    permission_classes = (DRYPermissions,)

    def get_permissions(self):
        if self.action in ['list']:
            permission_classes = []
        else:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]


class TaskTypeViewSet(viewsets.ModelViewSet):

    serializer_class = TaskTypeSerializer
    queryset = TaskType.objects.all()
    filter_fields = '__all__'
    permission_classes = (DRYPermissions,)

    def get_permissions(self):
        if self.action in ['list']:
            permission_classes = []
        else:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]


class EventViewSet(viewsets.ModelViewSet):

    serializer_class = EventSerializer
    queryset = Event.objects.all()
    filterset_fields = {
        'start_time': ['exact', 'gte', 'lte'],
        'end_time': ['exact', 'gte', 'lte'],
        'cell': ['exact'],
    }
    permission_classes = (DRYPermissions, DjangoFilterBackend)

    def get_permissions(self):
        if self.action in ['list']:
            permission_classes = []
        else:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]


class ParticipationFilterBackend(DRYPermissionFiltersBase):

    def filter_list_queryset(self, request, queryset, view):
        """
        Limits all list requests to only be seen by the staff or owner.
        """
        if request.user.is_staff:
            return queryset
        else:
            return queryset.filter(user=request.user)


class ParticipationViewSet(viewsets.ModelViewSet):

    serializer_class = ParticipationSerializer
    queryset = Participation.objects.all()
    filterset_fields = {
        'registered_at': ['exact', 'gte', 'lte'],
        'event__start_time': ['exact', 'gte', 'lte'],
        'event__end_time': ['exact', 'gte', 'lte'],
        'presence_status': ['exact'],
        'is_standby': ['exact']
    }
    permission_classes = (DRYPermissions,)
    filter_backends = (ParticipationFilterBackend, DjangoFilterBackend)
