import json
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from django.utils import timezone

from apiVolontaria.factories import UserFactory, AdminFactory
from volunteer.models import TaskType


class TaskTypesTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

        self.tasktype = TaskType.objects.create(
            name='TaskType 1',
        )

    def test_create_new_tasktype_with_permission(self):
        """
        Ensure we can create a new tasktype if we have the permission.
        """
        data = {
            'name': 'TaskType 3',
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('volunteer:tasktypes'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_new_tasktype_without_permission(self):
        """
        Ensure we can't create a new tasktype if we don't have the permission.
        """
        data = {
            'name': 'TaskType 3',
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('volunteer:tasktypes'),
            data,
            format='json',
        )

        content = {
            "detail": "You are not authorized to create a new tasktype."
        }
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_tasktype(self):
        """
        Ensure we can list all tasktypes.
        """

        data = [
            {
                "id": self.tasktype.id,
                "name": self.tasktype.name,
            }
        ]

        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('volunteer:tasktypes'))

        self.assertEqual(json.loads(response.content)['results'], data)
        self.assertEqual(json.loads(response.content)['count'], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
