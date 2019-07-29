import json
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from django.utils import timezone

from apiVolontaria.factories import UserFactory, AdminFactory
from ..models import TaskType


class TaskTypesIdTests(APITestCase):

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

    def test_retrieve_tasktype_id_not_exist(self):
        """
        Ensure we can't retrieve a TaskType that doesn't exist.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'volunteer:tasktypes_id',
                kwargs={'pk': 999},
            )
        )

        content = {"detail": "Not found."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_tasktype(self):
        """
        Ensure we can retrieve a TaskType.
        """

        data = {
            "id": self.tasktype.id,
            "name": self.tasktype.name,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'volunteer:tasktypes_id',
                kwargs={'pk': self.tasktype.id},
            )
        )

        self.assertEqual(json.loads(response.content), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_tasktype_with_permission(self):
        """
        Ensure we can update a specific TaskType.
        """

        data = {
            "id": self.tasktype.id,
            "name": "my new_name",
        }

        data_post = {
            "name": "my new_name",

        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'volunteer:tasktypes_id',
                kwargs={'pk': self.tasktype.id},
            ),
            data_post,
            format='json',
        )

        self.assertEqual(json.loads(response.content), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_tasktype_id_not_exist_with_permission(self):
        """
        Ensure we can update a specific TaskType.
        """

        self.client.force_authenticate(user=self.admin)

        data_post = {
            "name": "my new_name",

        }

        response = self.client.patch(
            reverse(
                'volunteer:tasktypes_id',
                kwargs={'pk': 999},
            ),
            data_post,
            format='json',
        )

        content = {"detail": "Not found."}

        self.assertEqual(json.loads(response.content), content)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_tasktype_without_permission(self):
        """
        Ensure we can't update a specific tasktype without permission.
        """

        data_post = {
            "name": "my new_name",

        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'volunteer:tasktypes_id',
                kwargs={'pk': self.tasktype.id},
            ),
            data_post,
            format='json',
        )

        content = {'detail': "You are not authorized to update a tasktype."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_tasktype_with_permission(self):
        """
        Ensure we can delete a specific TaskType.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'volunteer:tasktypes_id',
                kwargs={'pk': self.tasktype.id},
            ),
        )

        self.assertEqual(response.content, b'')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_tasktype_id_not_exist_with_permission(self):
        """
        Ensure we can delete a specific TaskType.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'volunteer:tasktypes_id',
                kwargs={'pk': 999},
            ),
        )

        content = {"detail": "Not found."}

        self.assertEqual(json.loads(response.content), content)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_tasktype_without_permission(self):
        """
        Ensure we can't delete a specific TaskType without permission.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            reverse(
                'volunteer:tasktypes_id',
                kwargs={'pk': self.tasktype.id},
            ),
        )

        content = {'detail': "You are not authorized to delete a tasktype."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
