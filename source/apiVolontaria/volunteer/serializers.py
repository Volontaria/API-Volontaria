from rest_framework import serializers
from volunteer import models


class CycleBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Cycle
        fields = (
            'id',
            'name',
            'start_date',
            'end_date',
        )
        read_only_fields = [
            'id',
        ]
