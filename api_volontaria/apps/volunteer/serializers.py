from rest_framework import serializers

from api_volontaria.apps.user.serializers import UserLightSerializer
from api_volontaria.apps.volunteer.models import (
    TaskType,
    Participation,
    Cell,
    Event,
)


class CellSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Cell
        fields = '__all__'


class TaskTypeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = TaskType
        fields = '__all__'


class ParticipationSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Participation
        fields = '__all__'

    def validate_user(self, value):
        """
        Check that the blog post is about Django.
        """
        if self.context['request'].user.is_staff:
            return value
        elif value == self.context['request'].user:
            return value
        else:
            raise serializers.ValidationError(
                "You don't have the right to create a participation for "
                "an other user"
            )

    def to_representation(self, instance):
        data = super(ParticipationSerializer, self).to_representation(instance)
        data['user'] = UserLightSerializer(
            instance.user,
            context={'request': self.context['request']}
        ).data
        data['event'] = EventSerializer(
            instance.event,
            context={'request': self.context['request']}
        ).data
        return data


class EventSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            'id',
            'url',
            'start_time',
            'end_time',
            'nb_volunteers_needed',
            'nb_volunteers_standby_needed',
            'nb_volunteers',
            'nb_volunteers_standby',
            'cell',
            'task_type',
        ]

    def to_representation(self, instance):
        data = super(EventSerializer, self).to_representation(instance)
        data['task_type'] = TaskTypeSerializer(
            instance.task_type,
            context={'request': self.context['request']}
        ).data
        data['cell'] = CellSerializer(
            instance.cell,
            context={'request': self.context['request']}
        ).data
        return data
