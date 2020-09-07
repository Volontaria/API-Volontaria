from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions, \
    DRYPermissionFiltersBase
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from api_volontaria.apps.position.models import (
    Position,
    Application,
)

from api_volontaria.apps.position.serializers import (
    PositionSerializer,
    ApplicationSerializer,
)


class PositionViewSet(viewsets.ModelViewSet):

    serializer_class = PositionSerializer
    queryset = Position.objects.all()
    filter_fields = '__all__'
    permission_classes = (DRYPermissions,)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = []
        else:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]


class ApplicationViewSet(viewsets.ModelViewSet):

    serializer_class = ApplicationSerializer
    queryset = Application.objects.all()
    filter_fields = '__all__'
    permission_classes = (DRYPermissions,)

    # def get_permissions(self):
    #     if self.action in ['list']:
    #         permission_classes = []
    #     else:
    #         permission_classes = [IsAdminUser]

    #     return [permission() for permission in permission_classes]


#TODO: determine whether classes below are required for Position or Application

# class ParticipationFilterBackend(DRYPermissionFiltersBase):

#     def filter_list_queryset(self, request, queryset, view):
#         """
#         Limits all list requests to only be seen by the staff or owner.
#         """
#         if request.user.is_staff:
#             return queryset
#         else:
#             return queryset.filter(user=request.user)


# class ParticipationViewSet(viewsets.ModelViewSet):

#     serializer_class = ParticipationSerializer
#     queryset = Participation.objects.all()
#     filterset_fields = {
#         'registered_at': ['exact', 'gte', 'lte'],
#         'event__start_time': ['exact', 'gte', 'lte'],
#         'event__end_time': ['exact', 'gte', 'lte'],
#         'presence_status': ['exact'],
#         'is_standby': ['exact']
#     }
#     permission_classes = (DRYPermissions,)
#     filter_backends = (ParticipationFilterBackend, DjangoFilterBackend)
