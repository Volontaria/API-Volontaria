from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import (
    DRYPermissions,
    DRYPermissionFiltersBase,
)
from api_volontaria.apps.page.serializers import (
    PageSerializer,
)
from .models import (
     Page,
)


class PageViewSet(viewsets.ModelViewSet):

    serializer_class = PageSerializer
    queryset = Page.objects.all()
    filterset_fields = {
        'key': ['exact'],
    }
    permission_classes = (DRYPermissions, DjangoFilterBackend)

    def get_permissions(self):
        if self.action in ['list']:
            permission_classes = []
        else:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]
