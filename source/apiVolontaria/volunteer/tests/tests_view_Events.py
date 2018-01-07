import json

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.utils import timezone

from apiVolontaria.factories import UserFactory, AdminFactory
from location.models import Address, StateProvince, Country
from ..models import Cell, Event, Cycle, TaskType


class EventsTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

        self.random_country = Country.objects.create(
            name="random country",
            iso_code="RC",
        )
        self.random_state_province = StateProvince.objects.create(
            name="random state",
            iso_code="RS",
            country=self.random_country,
        )
        self.address = Address.objects.create(
            address_line1='random address 1',
            postal_code='RAN DOM',
            city='random city',
            state_province=self.random_state_province,
            country=self.random_country,
        )
        self.cell = Cell.objects.create(
            name="my cell",
            address=self.address,
        )
        self.cycle = Cycle.objects.create(
            name="my cycle",
        )
        self.task_type = TaskType.objects.create(
            name="my tasktype",
        )

        start_date = timezone.now() - timezone.timedelta(
            minutes=100,
        )
        end_date = start_date + timezone.timedelta(
            minutes=50,
        )

        self.cycle_inactive = Cycle.objects.create(
            name="my cycle",
            start_date=start_date,
            end_date=end_date
        )

        # Some date INSIDE the cycle range
        start_date = start_date + timezone.timedelta(
            minutes=1,
        )
        end_date = end_date - timezone.timedelta(
            minutes=1,
        )

        self.event = Event.objects.create(
            cell=self.cell,
            cycle=self.cycle,
            task_type=self.task_type,
            start_date=start_date,
            end_date=end_date,
        )

        self.event_inactive = Event.objects.create(
            cell=self.cell,
            cycle=self.cycle_inactive,
            task_type=self.task_type,
            start_date=start_date,
            end_date=end_date,
        )

    def test_create_new_event_with_permission(self):
        """
        Ensure we can create a new event if we have the permission.
        """
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(
            minutes=100,
        )

        start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        data = {
            'cell_id': self.cell.id,
            'cycle_id': self.cycle.id,
            'task_type_id': self.task_type.id,
            'start_date': start_date,
            'end_date': end_date,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('volunteer:events'),
            data,
            format='json',
        )

        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(content['start_date'], start_date_str)
        self.assertEqual(content['end_date'], end_date_str)
        self.assertEqual(content['cycle']['id'], self.cycle.id)
        self.assertEqual(content['cell']['id'], self.cell.id)
        self.assertEqual(content['task_type']['id'], self.task_type.id)
        self.assertEqual(content['nb_volunteers_needed'], 0)
        self.assertEqual(content['nb_volunteers_standby_needed'], 0)
        self.assertEqual(content['nb_volunteers'], 0)
        self.assertEqual(content['nb_volunteers_standby'], 0)

        # Check the system doesn't return attributes not expected
        attributes = ['id', 'start_date', 'end_date', 'nb_volunteers_needed',
                      'nb_volunteers_standby_needed', 'volunteers', 'cell',
                      'cycle', 'task_type', 'nb_volunteers_standby',
                      'nb_volunteers']

        for key in content.keys():
            self.assertTrue(
                key in attributes,
                'Attribute "{0}" is not expected but is '
                'returned by the system.'.format(key),
            )
            attributes.remove(key)

        # Ensure the system returns all expected attributes
        self.assertTrue(
            len(attributes) == 0,
            'The system failed to return some '
            'attributes : {0}'.format(attributes),
        )

    def test_create_new_event_without_permission(self):
        """
        Ensure we can't create a new event if we don't have the permission.
        """
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(
            minutes=100,
        )

        data = {
            'cell': self.cell.id,
            'cycle': self.cycle.id,
            'task_type': self.task_type.id,
            'start_date': start_date,
            'end_date': end_date,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('volunteer:events'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        content = {"detail": "You are not authorized to create a new event."}
        self.assertEqual(json.loads(response.content), content)

    def test_list_events_with_permissions(self):
        """
        Ensure we can list all events.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse('volunteer:events'),
            format='json',
        )

        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['count'], 2)

        # Check the system doesn't return attributes not expected
        attributes = ['id', 'start_date', 'end_date', 'nb_volunteers_needed',
                      'nb_volunteers_standby_needed', 'volunteers', 'cell',
                      'cycle', 'task_type', 'nb_volunteers_standby',
                      'nb_volunteers']

        for key in content['results'][0].keys():
            self.assertTrue(
                key in attributes,
                'Attribute "{0}" is not expected but is '
                'returned by the system.'.format(key),
            )
            attributes.remove(key)

        # Ensure the system returns all expected attributes
        self.assertTrue(
            len(attributes) == 0,
            'The system failed to return some '
            'attributes : {0}'.format(attributes),
        )

    def test_list_events_without_permissions(self):
        """
        Ensure we can list only active event (is_active property)
        if we don't have some permissions.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse('volunteer:events'),
            format='json',
        )

        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['count'], 1)

        # Check the system doesn't return attributes not expected
        attributes = ['id', 'start_date', 'end_date', 'nb_volunteers_needed',
                      'nb_volunteers_standby_needed', 'volunteers', 'cell',
                      'cycle', 'task_type', 'nb_volunteers_standby',
                      'nb_volunteers']

        for key in content['results'][0].keys():
            self.assertTrue(
                key in attributes,
                'Attribute "{0}" is not expected but is '
                'returned by the system.'.format(key),
            )
            attributes.remove(key)

        # Ensure the system returns all expected attributes
        self.assertTrue(
            len(attributes) == 0,
            'The system failed to return some '
            'attributes : {0}'.format(attributes),
        )
