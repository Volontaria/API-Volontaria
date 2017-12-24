import json

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.utils import timezone

from apiVolontaria.factories import UserFactory, AdminFactory
from location.models import Address, StateProvince, Country
from ..models import Cell, Event, Cycle, TaskType


class EventsIdTests(APITestCase):

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

        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(
            minutes=100,
        )

        self.event = Event.objects.create(
            cell=self.cell,
            cycle=self.cycle,
            task_type=self.task_type,
            start_date=start_date,
            end_date=end_date,
        )

    def test_retrieve_event_id_not_exist(self):
        """
        Ensure we can't retrieve an event that doesn't exist.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'volunteer:events_id',
                kwargs={'pk': 999},
            ),
            format='json',
        )

        content = {"detail": "Not found."}

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), content)

    def test_retrieve_event(self):
        """
        Ensure we can retrieve an event.
        """

        start_date_str = self.event.start_date.\
            strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_date_str = self.event.end_date.\
            strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        data = {
            'id': self.event.id,
            'cell': self.event.cell.id,
            'cycle': self.event.cycle.id,
            'task_type': self.event.task_type.id,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'nb_volunteers_needed':
                self.event.nb_volunteers_needed,
            'nb_volunteers_standby_needed':
                self.event.nb_volunteers_standby_needed,
            'volunteers': [],
            'volunteers_standby': [],
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'volunteer:events_id',
                kwargs={'pk': self.event.id},
            )
        )

        self.assertEqual(json.loads(response.content), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_event_with_permission(self):
        """
        Ensure we can update a specific event.
        """
        start_date_str = self.event.start_date.\
            strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_date_str = self.event.end_date.\
            strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        data = {
            'id': self.event.id,
            'cell': self.event.cell.id,
            'cycle': self.event.cycle.id,
            'task_type': self.event.task_type.id,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'nb_volunteers_needed': 10,
            'nb_volunteers_standby_needed':
                self.event.nb_volunteers_standby_needed,
            'volunteers': [],
            'volunteers_standby': [],
        }

        data_post = {
            "nb_volunteers_needed": 10,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'volunteer:events_id',
                kwargs={'pk': self.event.id},
            ),
            data_post,
            format='json',
        )

        self.assertEqual(json.loads(response.content), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_event_without_permission(self):
        """
        Ensure we can't update a specific event without permission.
        """
        data_post = {
            "nb_volunteers_needed": 10,

        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'volunteer:events_id',
                kwargs={'pk': self.event.id},
            ),
            data_post,
            format='json',
        )

        content = {'detail': "You are not authorized to update an event."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_event_that_doesnt_exist(self):
        """
        Ensure we can't update a specific event if it doesn't exist.
        """
        data_post = {
            "nb_volunteers_needed": 10,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'volunteer:events_id',
                kwargs={'pk': 9999},
            ),
            data_post,
            format='json',
        )

        content = {'detail': "Not found."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_event_with_permission(self):
        """
        Ensure we can delete a specific event.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'volunteer:events_id',
                kwargs={'pk': self.event.id},
            ),
        )

        self.assertEqual(response.content, b'')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_event_without_permission(self):
        """
        Ensure we can't delete a specific event without permission.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            reverse(
                'volunteer:events_id',
                kwargs={'pk': self.event.id},
            ),
        )

        content = {'detail': "You are not authorized to delete an event."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_event_that_doesnt_exist(self):
        """
        Ensure we can't delete a specific event if it doesn't exist
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'volunteer:events_id',
                kwargs={'pk': 9999},
            ),
        )

        content = {'detail': "Not found."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
