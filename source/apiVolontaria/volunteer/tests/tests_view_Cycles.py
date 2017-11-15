from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from volunteer.models import Cycle
from apiVolontaria.factories import UserFactory, AdminFactory
from django.utils import timezone


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
                minutes=100
            ),
        )

    def test_create_new_cycle_with_permission(self):
        """
        Ensure we can create a new cycle if we have the permission.
        """
        data = {
            'name': 'Cycle 3',
            'start_date': self.cycle.start_date,
            'end_date': self.cycle.end_date,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('volunteer:cycles'),
            data,
            format='json',
        )

        print(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_new_cycle_without_permission(self):
        """
        Ensure we can't create a new cycle if we don'thave the permission.
        """
        data = {
            'name': 'Cycle 3',
            'start_date': self.cycle.start_date,
            'end_date': self.cycle.end_date,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('volunteer:cycles'),
            data,
            format='json',
        )

        content = {"detail": "You\'re not authorized to create a new cycle."}
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
