import json

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.contrib.auth.models import User

from ..models import ActivationToken


class UsersTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

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
