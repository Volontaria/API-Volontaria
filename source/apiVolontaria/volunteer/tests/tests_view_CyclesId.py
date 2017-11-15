from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from volunteer.models import Cycle
from apiVolontaria.factories import UserFactory, AdminFactory
from django.utils import timezone
import json


class CyclesIdTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

        self.cycle = Cycle.objects.create(
            name='Cycle 1',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(
                minutes=100,
            ),
        )

    def test_retrieve_cycle_id_not_exist(self):
        """
        Ensure we can't retrieve a cycle that doesn't exist.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'volunteer:cycles_id',
                kwargs={'pk': 999},
            )
        )

        content = {"detail": "Not found."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_cycle(self):
        """
        Ensure we can retrieve a cycle.
        """
        start_date = self.cycle.start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_date = self.cycle.end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        data = {
            "id": self.cycle.id,
            "name": self.cycle.name,
            "start_date": start_date,
            "end_date": end_date,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'volunteer:cycles_id',
                kwargs={'pk': self.cycle.id},
            )
        )

        self.assertEqual(json.loads(response.content), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_cycle_with_permission(self):
        """
        Ensure we can update a specific cycle.
        """
        start_date = self.cycle.start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_date = self.cycle.end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        data = {
            "id": self.cycle.id,
            "name": "my new_name",
            "start_date": start_date,
            "end_date": end_date,
        }

        data_post = {
            "name": "my new_name",

        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'volunteer:cycles_id',
                kwargs={'pk': self.cycle.id},
            ),
            data_post,
            format='json',
        )

        self.assertEqual(json.loads(response.content), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_cycle_without_permission(self):
        """
        Ensure we can't update a specific cycle without permission.
        """
        data_post = {
            "name": "my new_name",

        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'volunteer:cycles_id',
                kwargs={'pk': self.cycle.id},
            ),
            data_post,
            format='json',
        )

        content = {'detail': "You are not authorized to update a cycle."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_cycle_that_doesnt_exist(self):
        """
        Ensure we can't update a specific cycle if it doesn't exist.
        """
        start_date = self.cycle.start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_date = self.cycle.end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        data_post = {
            "name": "my new_name",

        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'volunteer:cycles_id',
                kwargs={'pk': 9999},
            ),
            data_post,
            format='json',
        )

        content = {'detail': "Not found."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_cycle_with_permission(self):
        """
        Ensure we can delete a specific cycle.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'volunteer:cycles_id',
                kwargs={'pk': self.cycle.id},
            ),
        )

        self.assertEqual(response.content, b'')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_cycle_without_permission(self):
        """
        Ensure we can't delete a specific cycle without permission.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            reverse(
                'volunteer:cycles_id',
                kwargs={'pk': self.cycle.id},
            ),
        )

        content = {'detail': "You are not authorized to delete a cycle."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_cycle_that_doesnt_exist(self):
        """
        Ensure we can't delete a specific cycle if it doesn't exist
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'volunteer:cycles_id',
                kwargs={'pk': 9999},
            ),
        )

        content = {'detail': "Not found."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
