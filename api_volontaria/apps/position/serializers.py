from rest_framework import serializers

from api_volontaria.apps.user.serializers import UserLightSerializer
from api_volontaria.apps.position.models import (
    Position,
    Application,
)


class PositionSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Position
        fields = '__all__'


class ApplicationSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Application
        fields = '__all__'

    def validate_user(self, value):
        """
        Check that the user creating a participation for another user
        either belongs to staff or is user himself.
        """
        if self.context['request'].user.is_staff:
            return value
        elif value == self.context['request'].user:
            return value
        else:
            raise serializers.ValidationError(
                "You don't have the right to create an application for "
                "an other user"
            )

    def to_representation(self, instance):
        data = super(ApplicationSerializer, self).to_representation(instance)
        data['user'] = UserLightSerializer(
            instance.user,
            context={'request': self.context['request']}
        ).data
        data['position'] = PositionSerializer(
            instance.position,
            context={'request': self.context['request']}
        ).data
        return data
