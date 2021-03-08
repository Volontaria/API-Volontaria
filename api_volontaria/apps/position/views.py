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


class ApplicationViewSet(viewsets.ModelViewSet):

    serializer_class = ApplicationSerializer
    queryset = Application.objects.all()
    filter_fields = '__all__'
    permission_classes = (DRYPermissions,)

    def get_queryset(self):
        if self.request.user.is_staff:
            return Application.objects.all()
        else:
            return Application.objects.filter(user=self.request.user)
