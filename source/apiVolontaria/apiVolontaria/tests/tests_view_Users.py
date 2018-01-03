import json

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.contrib.auth.models import User

from ..models import ActivationToken
from ..factories import UserFactory, AdminFactory


class UsersTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

    def test_create_new_user(self):
        """
        Ensure we can create a new user if we have the permission.
        """
        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': 'test123!',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username="John")
        activation_token = ActivationToken.objects.filter(user=user)

        self.assertEqual(1, len(activation_token))
        self.assertTrue(user.check_password(data['password']))

    def test_create_new_user_without_username(self):
        """
        Ensure we can't create a new user without username
        """
        data = {
            'email': 'John@mailinator.com',
            'password': 'test123!',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {"username": ["This field is required."]}
        self.assertEqual(json.loads(response.content), content)

    def test_create_new_user_without_email(self):
        """
        Ensure we can't create a new user without email
        """
        data = {
            'username': 'John',
            'password': 'test123!',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {"email": ["This field is required."]}
        self.assertEqual(json.loads(response.content), content)

    def test_create_new_user_without_password(self):
        """
        Ensure we can't create a new user without password
        """
        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {"password": ["This field is required."]}
        self.assertEqual(json.loads(response.content), content)

    def test_list_users(self):
        """
        Ensure we can list all users.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse('users'))

        self.assertEqual(json.loads(response.content)['count'], 2)

        first_user = json.loads(response.content)['results'][0]
        self.assertEqual(first_user['id'], self.user.id)

        # Check the system doesn't return attributes not expected
        attributes = ['id', 'username', 'email', 'first_name',
                      'last_name', 'is_active']
        for key in first_user.keys():
            self.assertTrue(
                key in attributes,
                'Attribute "{0}" is not expected but is '
                'returned by the system.'.format(key)
            )
            attributes.remove(key)

        # Ensure the system returns all expected attributes
        self.assertTrue(
            len(attributes) == 0,
            'The system failed to return some '
            'attributes : {0}'.format(attributes)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_without_authenticate(self):
        """
        Ensure we can't list users without authentication.
        """
        response = self.client.get(reverse('users'))

        content = {"detail": "Authentication credentials were not provided."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_without_permissions(self):
        """
        Ensure we can't list users without permissions.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('users'))

        content = {"detail": "You are not authorized to list users."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
