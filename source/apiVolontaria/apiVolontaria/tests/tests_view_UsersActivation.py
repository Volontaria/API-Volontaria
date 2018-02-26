import json

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.contrib.auth.models import User

from ..factories import UserFactory
from ..models import ActionToken


class UsersActivationTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.is_active = False
        self.user.save()

        self.activation_token = ActionToken.objects.create(
            user=self.user,
            type='account_activation',
        )

    def test_activate_user(self):
        """
        Ensure we can activate a user by using an ActionToken.
        """
        self.client.force_authenticate(user=self.user)

        data = {
            'activation_token': self.activation_token.key,
        }

        response = self.client.post(
            reverse('users_activation'),
            data,
            format='json',
        )

        # It's the good user
        self.assertEqual(json.loads(response.content)['id'], self.user.id)

        # We read a new time the user to be synchronized
        user_sync = User.objects.get(id=self.user.id)

        # The user is now active
        self.assertTrue(user_sync.is_active)

        # The token has been removed
        tokens = ActionToken.objects.filter(
            user=user_sync,
            type='account_activation',
        )
        self.assertTrue(len(tokens) == 0)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_activate_user_with_bad_token(self):
        """
        Ensure we can't activate a user without a good ActionToken.
        """
        self.client.force_authenticate(user=self.user)

        data = {
            'activation_token': 'bad_token',
        }

        response = self.client.post(
            reverse('users_activation'),
            data,
            format='json',
        )

        content = {'detail': '"bad_token" is not a valid activation_token.'}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
