import json

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.contrib.auth.models import User

from ..factories import UserFactory
from ..models import ActionToken


class ChangePasswordTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.is_active = False
        self.user.save()

        self.token = ActionToken.objects.create(
            user=self.user,
            type='password_change',
        )

    def test_change_password(self):
        """
        Ensure we can change a password with a valid token and a good password
        """
        data = {
            'token': self.token.key,
            'new_password': 'dWqq!Kld3#9dw'
        }

        response = self.client.post(
            reverse('change_password'),
            data,
            format='json',
        )

        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
            expired=False,
        )

        self.assertEqual(json.loads(response.content)['id'], self.user.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # We sync user after this change
        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.check_password('dWqq!Kld3#9dw'))

        self.assertTrue(len(tokens) == 0)

    def test_change_password_with_bad_token(self):
        """
        Ensure we can't change a password with an invalid token
        """
        data = {
            'token': 'test',
            'new_password': 'dWqq!Kld3#9dw'
        }

        response = self.client.post(
            reverse('change_password'),
            data,
            format='json',
        )

        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        content = {
            'non_field_errors': "test is not a valid token.",
        }
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(len(tokens) == 1)

        self.assertFalse(self.user.check_password('dWqq!Kld3#9dw'))

    def test_change_password_without_token(self):
        """
        Ensure we can't change a password without token
        """
        data = {
            'new_password': 'dWqq!Kld3#9dw'
        }

        response = self.client.post(
            reverse('change_password'),
            data,
            format='json',
        )

        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        content = {
            'token': ["This field is required."],
        }
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(len(tokens) == 1)

        self.assertFalse(self.user.check_password('dWqq!Kld3#9dw'))

    def test_change_password_with_an_empty_token(self):
        """
        Ensure we can't change a password with an empty token
        """
        data = {
            'token': '',
            'new_password': 'dWqq!Kld3#9dw'
        }

        response = self.client.post(
            reverse('change_password'),
            data,
            format='json',
        )

        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        content = {
            'token': ["This field may not be blank."],
        }
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(len(tokens) == 1)

        self.assertFalse(self.user.check_password('dWqq!Kld3#9dw'))

    def test_change_password_without_new_password(self):
        """
        Ensure we can't change a password without a new password
        """
        data = {
            'token': self.token.key,
        }

        response = self.client.post(
            reverse('change_password'),
            data,
            format='json',
        )

        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        content = {
            'new_password': ["This field is required."],
        }
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(len(tokens) == 1)

        self.assertFalse(self.user.check_password('dWqq!Kld3#9dw'))

    def test_change_password_with_an_empty_new_password(self):
        """
        Ensure we can't change a password without a valid new password
        """
        data = {
            'token': self.token.key,
            'new_password': '',
        }

        response = self.client.post(
            reverse('change_password'),
            data,
            format='json',
        )

        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        content = {
            'new_password': ["This field may not be blank."],
        }
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(len(tokens) == 1)

        self.assertFalse(self.user.check_password('dWqq!Kld3#9dw'))

    def test_change_password_with_a_weak_new_password(self):
        """
        Ensure we can't change a password with a weak new password
        """
        data = {
            'token': self.token.key,
            'new_password': 'akrent'
        }

        response = self.client.post(
            reverse('change_password'),
            data,
            format='json',
        )

        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        content = {
            'non_field_errors': [
                'This password is too short. '
                'It must contain at least 8 characters.',
            ],
        }
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(len(tokens) == 1)

        self.assertFalse(self.user.check_password('akrent'))
