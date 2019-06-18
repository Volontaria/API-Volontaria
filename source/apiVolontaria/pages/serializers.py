from rest_framework import serializers

from pages.models import InfoSection


class InfoPageSerializer(serializers.ModelSerializer):

    class Meta:
        model = InfoSection
        fields = (
            'id',
            'is_accordion',
            'title',
            'content',
        )
        read_only_fields = (
            'id',
            'is_accordion',
            'title',
            'content',
        )
