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
        self.second_cell = Cell.objects.create(
            name="my second cell",
            address=self.address,
        )
        self.cycle = Cycle.objects.create(
            name="my cycle",
        )
        self.second_cycle = Cycle.objects.create(
            name="my second cycle",
        )
        self.task_type = TaskType.objects.create(
            name="my tasktype",
        )
        self.second_task_type = TaskType.objects.create(
            name="my second tasktype",
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
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'volunteer:events_id',
                kwargs={'pk': self.event.id},
            )
        )

        result = json.loads(response.content)
        self.assertEqual(result['id'], self.event.id)
        self.assertEqual(result['cell']['id'], self.event.cell.id)
        self.assertEqual(result['cycle']['id'], self.event.cycle.id)
        self.assertEqual(result['task_type']['id'], self.event.task_type.id)
        self.assertEqual(
            result['nb_volunteers_needed'],
            self.event.nb_volunteers_needed
        )
        self.assertEqual(
            result['nb_volunteers_standby_needed'],
            self.event.nb_volunteers_standby_needed
        )
        self.assertEqual(
            result['nb_volunteers'],
            self.event.nb_volunteers
        )
        self.assertEqual(
            result['nb_volunteers_standby'],
            self.event.nb_volunteers_standby
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_event_with_permission(self):
        """
        Ensure we can update a specific event.
        """

        data_post = {
            "nb_volunteers_needed": 10,
            "cell_id": self.second_cell.id,
            "task_type_id": self.second_task_type.id,
        }

        self.admin.is_superuser = True
        self.admin.save()

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'volunteer:events_id',
                kwargs={'pk': self.event.id},
            ),
            data_post,
            format='json',
        )

        result = json.loads(response.content)

        self.assertEqual(result['id'], self.event.id)
        self.assertEqual(
            result['cell']['id'],
            self.second_cell.id,
        )
        self.assertEqual(
            result['task_type']['id'],
            self.second_task_type.id,
        )
        self.assertEqual(result['nb_volunteers_needed'], 10)
        self.assertEqual(
            result['nb_volunteers_standby_needed'],
            self.event.nb_volunteers_standby_needed,
        )
        self.assertEqual(
            result['nb_volunteers'],
            self.event.nb_volunteers
        )
        self.assertEqual(
            result['nb_volunteers_standby'],
            self.event.nb_volunteers_standby
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_update_event_cycle(self):
        """
        Ensure we can partially update a specific event.
        """

        data_post = {
            "cycle_id": self.second_cycle.id,
        }

        self.admin.is_superuser = True
        self.admin.save()

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'volunteer:events_id',
                kwargs={'pk': self.event.id},
            ),
            data_post,
            format='json',
        )

        result = json.loads(response.content)

        self.assertEqual(result['id'], self.event.id)
        self.assertEqual(
            result['cycle']['id'],
            self.second_cycle.id,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_event_start_date(self):
        """
        Ensure we can partially update a specific event.
        This test works since the associated cycle has nos start_date and
        end_date.
        """

        data_post = {
            "start_date": "2018-09-09T12:00:00Z",
        }

        self.admin.is_superuser = True
        self.admin.save()

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'volunteer:events_id',
                kwargs={'pk': self.event.id},
            ),
            data_post,
            format='json',
        )

        result = json.loads(response.content)

        self.assertEqual(result['id'], self.event.id)
        self.assertEqual(
            result['start_date'],
            "2018-09-09T12:00:00Z",
        )

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

        content = {
            'detail': 'You do not have permission to perform this action.'
        }
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

        content = {
            'detail': 'You do not have permission to perform this action.'
        }
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
