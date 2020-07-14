from rest_framework import viewsets

from apiVolontaria import permissions
from .models import (
     CKEditorPage
)

from . import serializers


class CKEditorPageViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.CKEditorPageSerializer
    queryset = CKEditorPage.objects.all()
    filterset_fields = '__all__'
    permission_classes = [permissions.IsAdminOrReadOnly]
