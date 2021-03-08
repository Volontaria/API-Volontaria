import json
from datetime import datetime

from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from djmoney.models.fields import MoneyField

from api_volontaria.apps.position.models import (
    Position,
    Application,
)
from api_volontaria.factories import (
    UserFactory,
    AdminFactory,
)
from api_volontaria.testClasses import CustomAPITestCase

import pytz
from django.conf import settings
LOCAL_TIMEZONE = pytz.timezone(settings.TIME_ZONE)


class PositionsTests(CustomAPITestCase):

    ATTRIBUTES = [
        'id',
        'url',
        'name',
        'description',
        'hourly_wage',
        'hourly_wage_currency',
        'weekly_hours',
        'minimum_days_commitment',
        'is_remote_job',
        'is_posted',
    ]

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

        self.position = Position.objects.create(
            hourly_wage=14.00,
            weekly_hours=15,
            minimum_days_commitment=3,
            is_remote_job=True,
            is_posted=True,
        )

        self.position2 = Position.objects.create(
            hourly_wage=14.50,
            weekly_hours=30.5,
            minimum_days_commitment=6.5,
            is_remote_job=False,
            is_posted=False,
        )

    def test_create_new_position_as_admin(self):
        """
        Ensure we can create a new position if we are an admin.
        """
        data_post = {
            "name": "My new position name",
            "description": "My new position description",
            "hourly_wage": 15.00,
            "hourly_wage_currency": "CAD",
            "weekly_hours": 40,
            "minimum_days_commitment": 6,
            "is_remote_job": True,
            "is_posted": True,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('position-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.check_attributes(content)

    def test_create_new_position(self):
        """
        Ensure we can't create a new position if we are a simple user.
        """
        data_post = {
            "name": "My new position name",
            "description": "My new position description",
            "hourly_wage": 15,
            "hourly_wage_currency": "CAD",
            "weekly_hours": 40,
            "minimum_days_commitment": 6,
            "is_remote_job": True,
            "is_posted": True,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('position-list'),
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

    def test_create_new_position_without_auth(self):
        """
        Ensure we can't create a new position if we are not logged in.
        """
        data_post = {
            "name": "My new position name",
            "description": "My new position description",
            "hourly_wage": 15,
            "hourly_wage_currency": "CAD",
            "weekly_hours": 40,
            "minimum_days_commitment": 6,
            "is_remote_job": True,
            "is_posted": True,
        }

        response = self.client.post(
            reverse('position-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertEqual(
            content,
            {
                'detail': 'Authentication credentials were not provided.'
            }
        )

    def test_update_position_as_admin(self):
        """
        Ensure we can update a position if we are an admin.
        """
        new_hourly_wage = 16.5
        data_post = {
            'hourly_wage': new_hourly_wage,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'position-detail',
                kwargs={
                    'pk': self.position.id
                },
            ),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_attributes(content)
        self.assertEqual(
            float(content['hourly_wage']),
            new_hourly_wage,
        )

    def test_update_position(self):
        """
        Ensure we can't update a position if we are a simple user.
        """
        new_hourly_wage = 16
        data_post = {
            'hourly_wage': new_hourly_wage,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'position-detail',
                kwargs={
                    'pk': self.position.id
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

    def test_update_position_without_user(self):
        """
        Ensure we can't update a position if we are not logged in.
        """
        new_hourly_wage = 16
        data_post = {
            'hourly_wage': new_hourly_wage,
        }

        response = self.client.patch(
            reverse(
                'position-detail',
                kwargs={
                    'pk': self.position.id
                },
            ),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            content,
            {
                'detail': 'Authentication credentials were not provided.'
            }
        )

    def test_delete_position_as_admin(self):
        """
        Ensure we can delete a position if we are an admin.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'position-detail',
                kwargs={
                    'pk': self.position.id
                },
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')

    def test_delete_position(self):
        """
        Ensure we can't delete a position if we are a simple user.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            reverse(
                'position-detail',
                kwargs={
                    'pk': self.position.id
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

    def test_delete_position_without_auth(self):
        """
        Ensure we can't delete a position if we are not logged in.
        """
        response = self.client.delete(
            reverse(
                'position-detail',
                kwargs={
                    'pk': self.position.id
                },
            )
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            content,
            {
                'detail': 'Authentication credentials were not provided.'
            }
        )

    def test_list_position(self):
        """
        Ensure positions can be listed by users.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse('position-list'),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content['results']), 2)
        self.check_attributes(content['results'][0])

    def test_list_position_without_auth(self):
        """
        Ensure positions can be listed without being logged in.
        """
        response = self.client.get(
            reverse('position-list'),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content['results']), 2)
        self.check_attributes(content['results'][0])
