from rest_framework import serializers

from django.db import IntegrityError

from location.serializers import (AddressBasicSerializer,
                                  StateProvinceBasicSerializer,
                                  CountryBasicSerializer)
from location.models import Address, StateProvince, Country
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
    """This class represents the TaskType model serializer."""

    class Meta:
        model = models.TaskType
        fields = (
            'id',
            'name',
        )
        read_only_fields = [
            'id',
        ]


class CellBasicSerializer(serializers.ModelSerializer):
    """This class represents the Cell model serializer."""

    address = serializers.DictField()

    def create(self, validated_data):
        cell = models.Cell()
        cell.name = validated_data['name']
        address_data = validated_data['address']
        country_data = validated_data['address']['country']
        state_province_data = validated_data['address']['state_province']

        address_data['country'] = country_data['iso_code']
        address_data['state_province'] = state_province_data['iso_code']

        try:
            cell_address = Address.objects.get(**address_data)
        except Address.DoesNotExist:
            try:
                cell_address = Address()
                cell_address.__dict__.update(validated_data['address'])
                cell_address.country, created = Country.objects.get_or_create(
                    name__iexact=country_data['name'],
                    iso_code__iexact=country_data['iso_code'],
                    defaults={
                        'iso_code': country_data['iso_code'],
                        'name': country_data['name'],
                    },
                )
            except IntegrityError as err:
                if 'UNIQUE constraint failed' in err.args[0]:
                    error = {
                        'message': (
                            "A Country with that iso_code already exists"
                            if err.args else "Unknown Error"
                        )
                    }
                    raise serializers.ValidationError(error)
            try:
                cell_address.state_province, created = (
                    StateProvince.objects.get_or_create(
                        iso_code__iexact=state_province_data['iso_code'],
                        name__iexact=state_province_data['name'],
                        country=cell_address.country,
                        defaults={
                            'iso_code': state_province_data['iso_code'],
                            'name': state_province_data['name'],
                        },
                    )
                )
                cell_address.save()
            except IntegrityError as err:
                if 'UNIQUE constraint failed' in err.args[0]:
                    error = {
                        'message': (
                            "A StateProvince with that iso_code already exists"
                            if err.args else "Unknown Error"
                        )
                    }
                    raise serializers.ValidationError(error)

        cell.address = cell_address
        cell.save()
        return cell

    def update(self, instance, validated_data):
        instance.name = validated_data['name']
        address_data = validated_data['address']
        country_data = validated_data['address']['country']
        state_province_data = validated_data['address']['state_province']

        address_data['country'] = country_data['iso_code']
        address_data['state_province'] = state_province_data['iso_code']

        try:
            cell_address = Address.objects.get(**address_data)
        except Address.DoesNotExist:
            try:
                cell_address = Address()
                cell_address.__dict__.update(validated_data['address'])
                cell_address.country, created = Country.objects.get_or_create(
                    name__iexact=country_data['name'],
                    iso_code__iexact=country_data['iso_code'],
                    defaults={
                        'iso_code': country_data['iso_code'],
                        'name': country_data['name'],
                    },
                )
            except IntegrityError as err:
                if 'UNIQUE constraint failed' in err.args[0]:
                    error = {
                        'message': (
                            "A Country with that iso_code already exists"
                            if err.args else "Unknown Error"
                        )
                    }
                    raise serializers.ValidationError(error)
            try:
                cell_address.state_province, created = (
                    StateProvince.objects.get_or_create(
                        iso_code__iexact=state_province_data['iso_code'],
                        name__iexact=state_province_data['name'],
                        country=cell_address.country,
                        defaults={
                            'iso_code': state_province_data['iso_code'],
                            'name': state_province_data['name'],
                        },
                    )
                )
                cell_address.save()
            except IntegrityError as err:
                if 'UNIQUE constraint failed' in err.args[0]:
                    error = {
                        'message': (
                            "A StateProvince with that iso_code already exists"
                            if err.args else "Unknown Error"
                        )
                    }
                    raise serializers.ValidationError(error)

        instance.address = cell_address

        instance.save()

        return instance

    def to_representation(self, instance):
        data = dict()
        data['id'] = instance.id
        data['name'] = instance.name
        data['address'] = AddressBasicSerializer(
            instance.address
        ).to_representation(instance.address)
        return data

    class Meta:
        model = models.Cell
        depth = 1
        fields = (
            'id',
            'name',
            'address',
        )
        read_only_fields = [
            'id',
        ]


class EventBasicSerializer(serializers.ModelSerializer):
    """This class represents the Event model serializer."""

    cell = CellBasicSerializer(read_only=True)
    cycle = CycleBasicSerializer(read_only=True)
    task_type = TaskTypeBasicSerializer(read_only=True)

    cell_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Cell.objects.all(),
        source='cell',
        write_only=True,
    )

    cycle_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Cycle.objects.all(),
        source='cycle',
        write_only=True,
    )

    task_type_id = serializers.PrimaryKeyRelatedField(
        queryset=models.TaskType.objects.all(),
        source='task_type',
        write_only=True,
    )

    class Meta:
        model = models.Event
        fields = (
            'id',
            'start_date',
            'end_date',
            'nb_volunteers_needed',
            'nb_volunteers_standby_needed',
            'volunteers',
            'volunteers_standby',
            'cell',
            'cycle',
            'task_type',
            'cell_id',
            'cycle_id',
            'task_type_id',
        )
        read_only_fields = [
            'id',
        ]
