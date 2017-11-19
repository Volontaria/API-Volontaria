from rest_framework import serializers

from . import models


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


class TaskTypeBasicSerializer(serializers.ModelSerializer):

    """

    This class represents the TaskType model serializer.

    A serializer will format the object prior to the interaction with the user.

    """

    class Meta:
        model = models.TaskType
        fields = (
            'id',
            'name',
        )
        read_only_fields = [
            'id',
        ]
