from rest_framework import serializers

from .models import (
    CKEditorPage
)


class CKEditorPageSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = CKEditorPage
        fields = '__all__'
