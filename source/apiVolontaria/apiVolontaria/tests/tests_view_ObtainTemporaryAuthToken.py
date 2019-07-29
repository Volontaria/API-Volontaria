import json

from rest_framework.test import APIClient

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from apiVolontaria.models import TemporaryToken
from apiVolontaria.factories import UserFactory


class ObtainTemporaryAuthTokenTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()
        self.url = reverse('token_api')

    def test_authenticate(self):
        """
        Ensure we can authenticate on the platform.
        """
        data = {
            'login': self.user.username,
            'password': 'Test123!'
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token = TemporaryToken.objects.get(
            user__username=self.user.username,
        )
        self.assertContains(response, token)

    def test_authenticate_expired_token(self):
        """
        Ensure we can authenticate on the platform when token is expired.
        """
        data = {
            'login': self.user.username,
            'password': 'Test123!'
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token_old = TemporaryToken.objects.get(
            user__username=self.user.username,
        )
        token_old.expire()

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token_new = TemporaryToken.objects.get(
            user__username=self.user.username,
        )

        self.assertNotContains(response, token_old)
        self.assertContains(response, token_new)

    def test_authenticate_bad_password(self):
        """
        Ensure we can't authenticate with a wrong password'
        """
        data = {
            'login': self.user.username,
            'password': 'test123!'  # No caps on the first letter
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        tokens = TemporaryToken.objects.filter(
            user__username='John'
        ).count()
        self.assertEqual(0, tokens)

    def test_authenticate_bad_username(self):
        """
        Ensure we can't authenticate with a wrong username
        """
        data = {
            'login': 'Jon',  # Forget the `h` in `John`
            'password': 'Test123!'
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        tokens = TemporaryToken.objects.filter(
            user__username='John'
        ).count()
        self.assertEqual(0, tokens)

    def test_authenticate_inactive(self):
        """
        Ensure we can't authenticate if user is inactive
        """
        data = {
            'login': self.user.username,
            'password': 'Test123!'
        }

        User.objects.filter(id=self.user.id).update(is_active=False)

        response = self.client.post(self.url, data, format='json')

        content = {
            "non_field_errors": [
                "Unable to log in with provided credentials."
                ]
            }

        self.assertEqual(json.loads(response.content), content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        tokens = TemporaryToken.objects.filter(
            user__username=self.user.username
        ).count()
        self.assertEqual(0, tokens)

    def test_authenticate_missing_parameter(self):
        """
        Ensure we can't authenticate if "login" is not provided.
        """
        data = {
            'password': 'Test123!'
        }

        response = self.client.post(self.url, data, format='json')

        content = {
            'login': [
                'This field is required.'
                ]
            }

        self.assertEqual(json.loads(response.content), content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        tokens = TemporaryToken.objects.filter(
            user__username=self.user.username
        ).count()
        self.assertEqual(0, tokens)
