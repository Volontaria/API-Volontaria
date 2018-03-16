from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from volunteer.models import Cycle
from apiVolontaria.factories import UserFactory, AdminFactory
from django.utils import timezone
import json


class CyclesTests(APITestCase):

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

        self.past_cycle = Cycle.objects.create(
            name='Cycle 2',
            start_date=timezone.now() - timezone.timedelta(
                days=10,
            ),
            end_date=timezone.now(),
        )

    def test_create_new_cycle_with_permission(self):
        """
        Ensure we can create a new cycle if we have the permission.
        """
        data = {
            'name': 'Cycle 3',
            'start_date': timezone.now(),
            'end_date': timezone.now() + timezone.timedelta(
                minutes=100,
            ),
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('volunteer:cycles'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_new_cycle_without_permission(self):
        """
        Ensure we can't create a new cycle if we don't have the permission.
        """
        data = {
            'name': 'Cycle 3',
            'start_date': timezone.now(),
            'end_date': timezone.now() + timezone.timedelta(
                minutes=100
            ),
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('volunteer:cycles'),
            data,
            format='json',
        )

        content = {"detail": "You are not authorized to create a new cycle."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_cycle(self):
        """
        Ensure we can list all cycles.
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

        response = self.client.get(reverse('volunteer:cycles'))

        self.assertEqual(json.loads(response.content)['results'][0], data)
        self.assertEqual(json.loads(response.content)['count'], 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_cycle_when_is_active_true(self):
        start_date = self.cycle.start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_date = self.cycle.end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        data = [
            {
                "id": self.cycle.id,
                "name": self.cycle.name,
                "start_date": start_date,
                "end_date": end_date,
            }
        ]

        self.client.force_authenticate(user=self.user)

        url = "{0}?is_active=True".format(
            reverse('volunteer:cycles')
        )

        response = self.client.get(url)

        self.assertEqual(json.loads(response.content)['results'], data)
        self.assertEqual(json.loads(response.content)['count'], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_cycle_when_is_active_false(self):
        start_date = self.past_cycle.start_date\
            .strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_date = self.past_cycle.end_date\
            .strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        data = [
            {
                "id": self.past_cycle.id,
                "name": self.past_cycle.name,
                "start_date": start_date,
                "end_date": end_date,
            }
        ]

        self.client.force_authenticate(user=self.user)

        url = "{0}?is_active=False".format(
            reverse('volunteer:cycles')
        )

        response = self.client.get(url)

        self.assertEqual(json.loads(response.content)['count'], 1)
        self.assertEqual(json.loads(response.content)['results'], data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_cycle_when_is_active_bad_input(self):
        start_date = self.cycle.start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_date = self.cycle.end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        data = {
            "id": self.cycle.id,
            "name": self.cycle.name,
            "start_date": start_date,
            "end_date": end_date,
        }

        self.client.force_authenticate(user=self.user)

        # 'bad' is not a good input
        url = "{0}?is_active=bad".format(
            reverse('volunteer:cycles')
        )

        response = self.client.get(url)

        self.assertEqual(json.loads(response.content)['results'][0], data)
        self.assertEqual(json.loads(response.content)['count'], 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
