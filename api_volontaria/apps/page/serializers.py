from rest_framework import serializers

from .models import (
    Page
)


class PageSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Page
        fields = '__all__'
