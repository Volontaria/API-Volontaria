from rest_framework import serializers

from django.db import IntegrityError

from location.serializers import AddressBasicSerializer
from location.models import Address, StateProvince, Country

from apiVolontaria.serializers import UserPublicSerializer
from django.contrib.auth.models import User

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
    managers = serializers.ListField(required=False)

    def create(self, validated_data):
        cell = models.Cell()
        cell.name = validated_data['name']
        if 'managers' in validated_data.keys():
            managers = validated_data['managers']
        else:
            managers = None
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

        list_manager = list()
        if managers:
            for manager in managers:
                try:
                    user = User.objects.get(id=manager)
                    list_manager.append(user)
                except Exception as err:
                    error = {
                        'message': (
                            "Unknown user with this ID"
                            if err.args else "Unknown Error"
                        )
                    }
                    raise serializers.ValidationError(error)

        cell.save()
        for user in list_manager:
            cell.managers.add(user)
        return cell

    def update(self, instance, validated_data):
        if 'name' in validated_data.keys():
            instance.name = validated_data['name']
        if 'managers' in validated_data.keys():
            # Remove all managers of the cell
            instance.managers.clear()

            for manager in validated_data['managers']:
                try:
                    user = User.objects.get(id=manager)
                    instance.managers.add(user)
                except Exception as err:
                    error = {
                        'message': (
                            "Unknown user with this ID"
                            if err.args else "Unknown Error"
                        )
                    }
                    raise serializers.ValidationError(error)
        if 'address' in validated_data.keys():
            try:
                address_data = validated_data['address']
                country_data = validated_data['address']['country']
                state_province_data = \
                    validated_data['address']['state_province']

                address_data['country'] = country_data['iso_code']
                address_data['state_province'] = \
                    state_province_data['iso_code']
            except KeyError as err:
                error = {
                    'message': (
                        "Please specify a complete valid address."
                        if err.args else "Unknown Error"
                    )
                }
                raise serializers.ValidationError(error)

            try:
                cell_address = Address.objects.get(**address_data)
            except Address.DoesNotExist:
                try:
                    cell_address = Address()
                    cell_address.__dict__.update(validated_data['address'])
                    cell_address.country, created = \
                        Country.objects.get_or_create(
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
                                "A StateProvince with "
                                "that iso_code already exists"
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
        data['managers'] = list()
        for manager in instance.managers.all():
            data['managers'].append(
                UserPublicSerializer(
                    manager
                ).to_representation(manager)
            )
        return data

    class Meta:
        model = models.Cell
        depth = 1
        fields = (
            'id',
            'name',
            'address',
            'managers'
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
            'nb_volunteers',
            'nb_volunteers_standby_needed',
            'nb_volunteers_standby',
            'volunteers',
            'cell',
            'cycle',
            'task_type',
            'cell_id',
            'cycle_id',
            'task_type_id',
        )
        read_only_fields = [
            'id',
            'subscription_date',
            'nb_volunteers',
            'nb_volunteers_standby',
        ]


class ParticipationBasicSerializer(serializers.ModelSerializer):
    """This class represents the Participation model serializer."""

    # Explicitly declare the BooleanField to make it "required"
    standby = serializers.BooleanField()
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = models.Participation
        fields = (
            'id',
            'event',
            'user',
            'standby',
            'subscription_date',
        )
        read_only_fields = [
            'id',
        ]
