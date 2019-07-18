import json

from unittest import mock

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.test.utils import override_settings

from ..factories import UserFactory
from ..models import ActionToken

from django.core import mail
from anymail.exceptions import AnymailCancelSend
from anymail.signals import pre_send
from django.dispatch import receiver

@override_settings(EMAIL_BACKEND='anymail.backends.test.EmailBackend')
class ResetPasswordTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.is_active = False
        self.user.save()

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "FRONTEND_INTEGRATION": {
                "FORGOT_PASSWORD_URL": "fake_url",
            }
        }
    )
    def test_create_new_token(self):
        """
        Ensure we can have a new token to change our password
        """
        data = {
            'username_email': self.user.username,
        }

        response = self.client.post(
            reverse('reset_password'),
            data,
            format='json',
        )

        # Test that one message was sent:
        self.assertEqual(len(mail.outbox), 1)

        # The token has been created
        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        self.assertEqual(response.content, b'')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(len(tokens) == 1)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "FRONTEND_INTEGRATION": {
                "FORGOT_PASSWORD_URL": "fake_url",
            }
        }
    )
    def test_create_new_token_with_email(self):
        """
        Ensure we can have a new token to change our password
        """
        data = {
            'username_email': self.user.email,
        }

        response = self.client.post(
            reverse('reset_password'),
            data,
            format='json',
        )

        # Test that one message was sent:
        self.assertEqual(len(mail.outbox), 1)

        # The token has been created
        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        self.assertEqual(response.content, b'')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(len(tokens) == 1)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "FRONTEND_INTEGRATION": {
                "FORGOT_PASSWORD_URL1": "fake_url",
            }
        }
    )
    def test_create_new_token_with_call_exception(self):
        """
        Ensure we can not have a new token to change our password because exception
        """
        data = {
            'username_email': self.user.username,
        }

        response = self.client.post(
            reverse('reset_password'),
            data,
            format='json',
        )

        # The token has been created
        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )
        content = {
            'detail': "Your token has been created but no email "
                                "has been sent. Please contact the "
                                "administration."
        }

        self.assertEqual(json.loads(response.content), content)
        # Test that one message was sent:
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(len(tokens) == 1)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "FRONTEND_INTEGRATION": {
                "FORGOT_PASSWORD_URL": "fake_url",
            }
        }
    )
    def test_create_new_token_without_username_param(self):
        """
        Ensure we can't have a new token to change our password without
        give our username in param
        """
        data = dict()

        response = self.client.post(
            reverse('reset_password'),
            data,
            format='json',
        )

        # The token has been created
        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        content = {
            'username_email': ['This field is required.']
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(len(tokens) == 0)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "FRONTEND_INTEGRATION": {
                "FORGOT_PASSWORD_URL": "fake_url",
            }
        }
    )
    def test_create_new_token_with_an_empty_username_param(self):
        """
        Ensure we can't have a new token to change our password without
        give our username in param
        """
        data = {
            'username_email': '',
        }

        response = self.client.post(
            reverse('reset_password'),
            data,
            format='json',
        )

        # The token has been created
        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        content = {
            'username_email': ["This field may not be blank."],
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(len(tokens) == 0)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "FRONTEND_INTEGRATION": {
                "FORGOT_PASSWORD_URL": "fake_url",
            }
        }
    )
    def test_create_new_token_with_bad_username(self):
        """
        Ensure we can't have a new token to change our password without
        a valid username
        """
        data = {
            'username_email': 'test',
        }

        response = self.client.post(
            reverse('reset_password'),
            data,
            format='json',
        )

        # The token has been created
        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        content = {
            'username_email': ["No account with this username or email."],
        }
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(len(tokens) == 0)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "FRONTEND_INTEGRATION": {
                "FORGOT_PASSWORD_URL": "fake_url",
            }
        },
    )
    def test_create_new_token_when_token_already_exist(self):
        """
        Ensure we can have a new token to change our password
        """
        # We create a token before launch the test
        ActionToken.objects.create(
            user=self.user,
            type='password_change',
        )

        data = {
            'username_email': self.user.username,
        }

        response = self.client.post(
            reverse('reset_password'),
            data,
            format='json',
        )

        # Test that one message was sent:
        self.assertEqual(len(mail.outbox), 1)

        # The token has been created
        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
            expired=False,
        )

        self.assertEqual(response.content, b'')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(len(tokens) == 1)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": False,
            "FRONTEND_INTEGRATION": {
                "FORGOT_PASSWORD_URL": "fake_url",
            }
        }
    )
    def test_create_new_token_without_email_service(self):
        """
        Ensure we can have a new token to change our password
        """
        data = {
            'username_email': self.user.username,
        }

        response = self.client.post(
            reverse('reset_password'),
            data,
            format='json',
        )

        # Test that one message was not sent:
        self.assertEqual(len(mail.outbox), 0)

        # The token has been created
        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        self.assertEqual(response.content, b'')

        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)

        self.assertTrue(len(tokens) == 0)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "FRONTEND_INTEGRATION": {
                "FORGOT_PASSWORD_URL": "fake_url",
            }
        },
    )
    def test_create_new_token_with_failure_email(self):
        """
        Ensure we can nt send email after create new token
        """
        data = {
            'username_email': self.user.username,
        }

        @receiver(pre_send, weak=False)
        def cancel_pre_send(sender, message, esp_name, **kwargs):
            raise AnymailCancelSend("whoa there")

        self.addCleanup(pre_send.disconnect, receiver=cancel_pre_send)

        response = self.client.post(
            reverse('reset_password'),
            data,
            format='json',
        )

        # Test that one message wasn't sent:
        self.assertEqual(len(mail.outbox), 0)

        # The token has been created
        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        content = {
            'detail': "Your token has been created but no email has " 
                       "been sent. Please contact the administration."
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(len(tokens) == 1)




