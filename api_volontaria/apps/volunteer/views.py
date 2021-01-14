import json
from io import TextIOWrapper

from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions, \
    DRYPermissionFiltersBase

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from api_volontaria.apps.volunteer.helpers import (
    InvalidBulkUpdate,
    add_bulk_from_file,
    AddBulkConfig
)
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
        if self.action in ['list', 'retrieve']:
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
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get_permissions(self):
        if self.action in ['list']:
            permission_classes = []
        else:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'])
    def bulk(self, request):
        """
        Bulk add of events using a file
        """
        file_data_bytes = request.data.get("file", None)
        if not file_data_bytes:
            return Response(
                {'file': ["No file was provided for bulk event creation"]},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            mapping = json.loads(request.data.get("mapping", "{}"))
        except ValueError as e:
            message = {
                "mapping":
                    [f"Mapping should be a dictionary "
                     f"represented in json, errors: {e}"]
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(mapping, dict):
            message = {
                "mapping":
                    ["Mapping should be a dictionary pairing the "
                     "csv column (key) to the element key (value)"]
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        config = AddBulkConfig(
            EventSerializer,
            request.data.get("format", "csv"),
            mapping
        )

        file_data = TextIOWrapper(file_data_bytes, encoding='utf-8')
        try:
            ids = add_bulk_from_file(file_data, config)
        except InvalidBulkUpdate as e:
            return Response(
                {"non_field_errors": [e.error]},
                status=status.HTTP_400_BAD_REQUEST
            )

        url_ids = [reverse('event-detail', kwargs={'pk': id_}) for id_ in ids]
        return Response({"created": url_ids}, status=status.HTTP_201_CREATED)


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
