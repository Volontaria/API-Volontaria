from rest_framework import serializers

from . import models


class CountryBasicSerializer(serializers.ModelSerializer):
    """This class represents the Country model serializer."""

    class Meta:
        model = models.Country
        fields = (
            'iso_code',
            'name',
        )


class StateProvinceBasicSerializer(serializers.ModelSerializer):
    """This class represents the StateProvince model serializer."""

    def to_representation(self, instance):
        data = dict()
        data['country'] = CountryBasicSerializer(
            instance.country
        ).to_representation(instance.country)
        return dict(
            iso_code=instance.iso_code,
            name=instance.name,
            **data
        )

    class Meta:
        model = models.StateProvince
        fields = (
            'iso_code',
            'name',
            'country',
        )


class AddressBasicSerializer(serializers.ModelSerializer):
    """This class represents the Address model serializer."""

    def to_representation(self, instance):
        data = dict()
        data['country'] = CountryBasicSerializer(
            instance.country
        ).to_representation(instance.country)
        data['state_province'] = StateProvinceBasicSerializer(
            instance.state_province
        ).to_representation(instance.state_province)
        data['state_province'].pop('country')
        return dict(
            id=instance.id,
            address_line1=instance.address_line1,
            address_line2=instance.address_line2,
            postal_code=instance.postal_code,
            city=instance.city,
            **data,
        )

    class Meta:
        model = models.Address
        fields = (
            'id',
            'address_line1',
            'address_line2',
            'postal_code',
            'city',
            'state_province',
            'country',
        )
