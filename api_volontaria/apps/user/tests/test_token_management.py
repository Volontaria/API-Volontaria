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

# from ..models import  ActionToken
from ..models import APIToken

User = get_user_model()


class AdminTests(CustomAPITestCase):

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
        # self.user = UserFactory()
        self.user = AdminFactory()
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
                'create': True,
            },
            'event': {
                'create': True,
            },
            'participation': {
                'create': True,
                'update': True,
                'destroy': True,
            },
            'tasktype': {
                'create': True,
            },
            'application': {
                'create': True,
                'update': True,
                'destroy': True,
            },
            'position': {
                'create': True,
                'update': True,
                'destroy': True,
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


    # Testing temporary token
    # see https://github.com/encode/django-rest-framework/blob/d635bc9c71b6cf84d137a68610ae2e628f8b62b3/docs/api-guide/testing.md

    # key = '401f7ac837da42b97f613d789819ff93537bee6a'

    def test_error_if_temporary_token_does_not_exist(self):

        self.client.force_authenticate(user=self.user, token='401f7ac837da42b97f613d789819ff93537bee6a')
        
        # token = ActionToken.objects.get(user__email=self.user.email)
        token = APIToken.objects.get(user__email=self.user.email)

        print(token)

        # token = ActionToken.objects.filter()

        # token = ActionToken.objects.get(user__email=self.user.email)
        
        # token = TemporaryTokenAuthentication

        # token.user, token = self.client.authenticate_credentials()


        # print(token)

        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        # print(self.client.credentials)
        # # response = self.client.get(self.user.auth_token)

        # print(self.user.auth_token)

        # self.assertEqual(
        #     response.status_code,
        #     status.HTTP_404_NOT_FOUND
        # )
        
# self.assertRaises

