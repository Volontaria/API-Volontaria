from rest_framework import serializers

from api_volontaria.apps.user.serializers import UserLightSerializer
from api_volontaria.apps.position.models import (
    Position,
    Application,
)


#TODO: consider whether functions should be defined for the classes below (validate_user and to_representation)


class PositionSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Position
        fields = '__all__'

    def validate_user(self, value):
        """
        Check that the user creating a position belongs to staff.
        """
        if self.context['request'].user.is_staff:
            return value
        else:
            raise serializers.ValidationError(
                "You don't have the right to create a position."
            )


class ApplicationSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Application
        fields = '__all__'