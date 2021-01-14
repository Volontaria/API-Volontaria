import json

from datetime import timedelta
from unittest import mock

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.test.utils import override_settings
from django.contrib.auth import get_user_model

from api_volontaria.factories import UserFactory, AdminFactory
from ..models import ActionToken
from ....testClasses import CustomAPITestCase

User = get_user_model()


class UsersTests(CustomAPITestCase):

    ATTRIBUTES = [
        'is_staff',
        'last_login',
        'date_joined',
        'groups',
        'user_permissions',
        'url',
        'id',
        'is_superuser',
        'last_name',
        'is_active',
        'first_name',
        'permissions',
        'email'
    ]

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

    def test_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            'http://api.example.org/rest-auth/user/'
        )

        # HTTP code is good
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.content
        )

        # Number of results is good
        content = json.loads(response.content)

        self.check_attributes(content)
        permissions = {
            'cell': {
                'create': False,
            },
            'event': {
                'create': False,
            },
            'participation': {
                'create': True,
                'update': False,
                'destroy': False,
            },
            'tasktype': {
                'create': False,
            },
            'application': {
                'create': True,
                'update': False,
                'destroy': False,
            },
            'position': {
                'create': False,
                'update': False,
                'destroy': False,
            },
        }
        self.assertEqual(
            content['permissions'],
            permissions
        )

    def test_register(self):
        response = self.client.post(
            'http://api.example.org/rest-auth/registration/',
            {
                'password1': 'test123!',
                'password2': 'test123!',
                'email': 'test@test.ca',
            }
        )

        # HTTP code is good
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.content
        )

        # Number of results is good
        content = json.loads(response.content)

        self.check_attributes(content, ['key'])

    def test_login(self):
        response = self.client.post(
            'http://api.example.org/rest-auth/login/',
            {
                'email': self.user.email,
                'password': 'Test123!',
            }
        )

        # HTTP code is good
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.content
        )

        # Number of results is good
        content = json.loads(response.content)

        self.check_attributes(content, ['key'])

    def test_logout(self):
        response = self.client.post(
            'http://api.example.org/rest-auth/logout/',
        )

        # HTTP code is good
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.content
        )

        # Number of results is good
        content = json.loads(response.content)

        self.assertEqual(
            content,
            {'detail': 'Successfully logged out.'}
        )

    def test_password_reset(self):
        response = self.client.post(
            'http://api.example.org/rest-auth/password/reset/',
            {
                'email': self.user.email
            }
        )

        # HTTP code is good
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.content
        )

        # Number of results is good
        content = json.loads(response.content)

        self.assertEqual(
            content,
            {'detail': 'Password reset e-mail has been sent.'}
        )

    def test_password_change(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            'http://api.example.org/rest-auth/password/change/',
            {
                'new_password1': 'Test1234!&',
                'new_password2': 'Test1234!&',
                'old_password': 'Test123!',
            }
        )

        # HTTP code is good
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.content
        )

        # Number of results is good
        content = json.loads(response.content)

        self.assertEqual(
            content,
            {'detail': 'New password has been saved.'}
        )

    def test_password_change_but_too_weak(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            'http://api.example.org/rest-auth/password/change/',
            {
                'new_password1': 'test',
                'new_password2': 'test',
                'old_password': 'Test123!',
            }
        )

        # HTTP code is good
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.content
        )

        # Number of results is good
        content = json.loads(response.content)

        self.assertEqual(
            content,
            {
                "new_password2": [
                    "This password is too short. It must contain "
                    "at least 8 characters.",
                    "This password is too common."
                ]
            }
        )

    def test_password_change_but_wrong_old_password(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            'http://api.example.org/rest-auth/password/change/',
            {
                'new_password1': 'Test123!',
                'new_password2': 'Test123!',
                'old_password': 'IForgotMyPassword',
            }
        )

        # HTTP code is good
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.content
        )

        # Number of results is good
        content = json.loads(response.content)

        self.assertEqual(
            content,
            {"old_password": ["Invalid password"]}
        )
