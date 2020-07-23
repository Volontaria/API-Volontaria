import json

from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse

from api_volontaria.apps.volunteer.models import (
    TaskType,
)
from api_volontaria.factories import (
    UserFactory,
    AdminFactory,
)
from api_volontaria.testClasses import CustomAPITestCase


class TaskTypesTests(CustomAPITestCase):

    ATTRIBUTES = [
        'id',
        'url',
        'name',
    ]

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

        self.tasktype = TaskType.objects.create(
            name='My new tasktype',
        )

    def test_create_new_task_type_as_admin(self):
        """
        Ensure we can create a new task type if we are an admin.
        """
        data_post = {
            'name': 'New task type',
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('tasktype-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.check_attributes(content)

    def test_create_new_task_type(self):
        """
        Ensure we can't create a new task type if we are a simple user.
        """
        data_post = {
            'name': 'New task type',
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('tasktype-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            content,
            {
                'detail': 'You do not have permission to perform this action.'
            }
        )

    def test_update_task_type_as_admin(self):
        """
        Ensure we can update a task type if we are an admin.
        """
        new_name = 'New task type updated name'
        data_post = {
            'name': new_name,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'tasktype-detail',
                kwargs={
                    'pk': self.tasktype.id
                },
            ),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_attributes(content)
        self.assertEqual(content['name'], new_name)

    def test_update_task_type(self):
        """
        Ensure we can't update a task type if we are a simple user.
        """
        new_name = 'New task type updated name'
        data_post = {
            'name': new_name,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'tasktype-detail',
                kwargs={
                    'pk': self.tasktype.id
                },
            ),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            content,
            {
                'detail': 'You do not have permission to perform this action.'
            }
        )

    def test_delete_task_type_as_admin(self):
        """
        Ensure we can delete a task type if we are an admin.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'tasktype-detail',
                kwargs={
                    'pk': self.tasktype.id
                },
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')

    def test_delete_task_type(self):
        """
        Ensure we can't delete a task type if we are a simple user.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'tasktype-detail',
                kwargs={
                    'pk': self.tasktype.id
                },
            )
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            content,
            {
                'detail': 'You do not have permission to perform this action.'
            }
        )

    def test_list_task_types(self):
        """
        Ensure we can list task types.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse('tasktype-list'),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content['results']), 1)
        self.check_attributes(content['results'][0])
