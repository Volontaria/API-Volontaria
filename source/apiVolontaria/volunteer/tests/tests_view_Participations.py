import json

from unittest import mock

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import Permission

from apiVolontaria.factories import UserFactory, AdminFactory
from location.models import Address, StateProvince, Country
from volunteer.models import Cell, Event, Cycle, TaskType, Participation


class ParticipationsTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.user2 = UserFactory()
        self.user2.set_password('Test123!')
        self.user2.save()

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
            end_date=end_date,
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

        self.event2 = Event.objects.create(
            cell=self.cell,
            cycle=self.cycle,
            task_type=self.task_type,
            start_date=start_date,
            end_date=end_date,
        )

        subscription_date = timezone.now()

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = subscription_date
            self.participation = Participation.objects.create(
                standby=True,
                user=self.user,
                event=self.event2,
            )

            self.participation2 = Participation.objects.create(
                standby=True,
                user=self.user2,
                event=self.event2,
            )

            self.participation3 = Participation.objects.create(
                standby=True,
                user=self.user2,
                event=self.event,
            )

    def test_create_new_participation(self):
        """
        Ensure we can create a new participation.
        """
        subscription_date = timezone.now()

        subscription_date_str = subscription_date.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ",
        )

        data = {
            'event': self.event.id,
            'user': self.user.id,
            'standby': False,
            'subscription_date': subscription_date,
        }

        self.client.force_authenticate(user=self.user)

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = subscription_date
            response = self.client.post(
                reverse('volunteer:participations'),
                data,
                format='json',
            )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(content['subscription_date'], subscription_date_str)
        self.assertEqual(content['user']['id'], self.user.id)
        self.assertEqual(content['event'], self.event.id)
        self.assertEqual(content['standby'], False)

        # Check the system doesn't return attributes not expected
        attributes = [
            'id',
            'subscription_date',
            'user',
            'event',
            'standby',
            'presence_duration_minutes',
            'presence_status',
        ]

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

    def test_create_duplicate_participation(self):
        """
        Ensure we can't create a duplicated participation.
        """
        subscription_date = timezone.now()

        data = {
            'event': self.event2.id,
            'standby': False,
        }

        self.client.force_authenticate(user=self.user)

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = subscription_date
            response = self.client.post(
                reverse('volunteer:participations'),
                data,
                format='json',
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {
            'non_field_errors': [
                'The fields event, user must make a unique set.',
            ],
        }
        self.assertEqual(json.loads(response.content), content)

    def test_list_participations(self):
        """
        Ensure we can list all participations.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse('volunteer:participations'),
            format='json',
        )

        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['count'], 3)

        # Check the system doesn't return attributes not expected
        attributes = [
            'id',
            'user',
            'event',
            'subscription_date',
            'standby',
            'presence_duration_minutes',
            'presence_status',
        ]

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

    def test_list_participations_filtered_by_username(self):
        """
        Ensure we can filter permissions by username.
        """
        self.client.force_authenticate(user=self.user)

        url = "{0}?username={1}".format(
            reverse('volunteer:participations'),
            self.user.username,
        )

        response = self.client.get(
            url,
            format='json',
        )

        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['count'], 1)
        self.assertEqual(content['results'][0]['id'], self.participation.id)

        # Check the system doesn't return attributes not expected
        attributes = [
            'id',
            'user',
            'event',
            'subscription_date',
            'standby',
            'presence_duration_minutes',
            'presence_status',
        ]

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

    def test_list_participations_filter_by_event(self):
        """
        Ensure we can list participations filtered by event.
        """
        self.client.force_authenticate(user=self.admin)

        url = "{0}?event={1}".format(
            reverse('volunteer:participations'),
            self.event.id,
        )

        response = self.client.get(
            url,
            format='json',
        )

        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['count'], 1)
