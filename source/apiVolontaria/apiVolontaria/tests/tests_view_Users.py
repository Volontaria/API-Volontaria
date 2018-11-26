import json

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.test.utils import override_settings
from django.contrib.auth.models import User

from ..models import ActionToken
from location.models import Address, StateProvince, Country
from volunteer.models import Cell, Event, Cycle, TaskType, Participation
from ..factories import UserFactory, AdminFactory
from django.core import mail

from anymail.exceptions import AnymailCancelSend
from anymail.signals import pre_send
from django.dispatch import receiver

@override_settings(EMAIL_BACKEND='anymail.backends.test.EmailBackend')
class UsersTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

        self.user_cell_manager = UserFactory()
        self.user_cell_manager.set_password('Test123!')

        self.random_country = Country.objects.create(
            name="random country",
            iso_code="RC",
        )
        self.random_state_province = StateProvince.objects.create(
            name="random state",
            iso_code="RS",
            country=self.random_country,
        )
        self.address = Address.objects.create(
            address_line1='random address 1',
            postal_code='RAN DOM',
            city='random city',
            state_province=self.random_state_province,
            country=self.random_country,
        )
        self.cell = Cell.objects.create(
            name="my cell",
            address=self.address,
        )
        self.cell_with_manager = Cell.objects.create(
            name="my cell with manager",
            address=self.address,
        )

        self.cell_with_manager.managers.set([self.user_cell_manager])
        self.cell_with_manager.save()

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": False,
            "AUTO_ACTIVATE_USER": False,
            "FRONTEND_INTEGRATION": {
                "ACTIVATION_URL": "fake_url",
            }
        }
    )
    def test_create_new_user_without_service_email(self):
        """
        Ensure we can create a new user if we have the permission even if the
        email service is not activated
        """
        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'phone': '1234567890',
            'first_name': 'Chuck',
            'last_name': 'Norris',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        content = {"detail": "The account was created but no email was sent "
                             "(email service deactivated). If your account is "
                             "not activated, contact the administration."}
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), content)

        user = User.objects.get(username="John")
        activation_token = ActionToken.objects.filter(
            user=user,
            type='account_activation',
        )

        self.assertEqual(1, len(activation_token))

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "AUTO_ACTIVATE_USER": False,
            "FRONTEND_INTEGRATION": {
                "ACTIVATION_URL": "fake_url",
            }
        }
    )
    def test_create_new_user(self):
        """
        Ensure we can create a new user if we have the permission.
        """
        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'phone': '1234567890',
            'first_name': 'Chuck',
            'last_name': 'Norris',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content)['phone'], '1234567890')

        user = User.objects.get(username="John")
        activation_token = ActionToken.objects.filter(
            user=user,
            type='account_activation',
        )

        self.assertEqual(1, len(activation_token))

    def test_create_new_user_without_profile_attributes(self):
        """
        Ensure we can create a new user without profile attributes.
        """
        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'first_name': 'Chuck',
            'last_name': 'Norris',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        content = {
            'non_field_errors': [
                'You must specify "phone" or "mobile" field.'
            ]
        }
        self.assertEqual(json.loads(response.content), content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_new_user_without_username(self):
        """
        Ensure we can't create a new user without username
        """
        data = {
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'first_name': 'Chuck',
            'last_name': 'Norris',
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
            'first_name': 'Chuck',
            'last_name': 'Norris',
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
            'first_name': 'Chuck',
            'last_name': 'Norris',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {"password": ["This field is required."]}
        self.assertEqual(json.loads(response.content), content)

    def test_create_new_user_weak_password(self):
        """
        Ensure we can't create a new user with a weak password
        """
        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': '19274682736',
            'first_name': 'Chuck',
            'last_name': 'Norris',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {"password": ['This password is entirely numeric.']}
        self.assertEqual(json.loads(response.content), content)

    def test_create_new_user_invalid_phone(self):
        """
        Ensure we can't create a new user with an invalid phone number
        """
        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': '19274682736',
            'phone': '12345',
            'mobile': '23445dfg',
            'first_name': 'Chuck',
            'last_name': 'Norris',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {
            "phone": ['Invalid format.'],
            "mobile": ['Invalid format.']
        }
        self.assertEqual(json.loads(response.content), content)

    def test_create_new_user_duplicate_email(self):
        """
        Ensure we can't create a new user with an already existing email
        """

        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'phone': '1234567890',
            'first_name': 'Chuck',
            'last_name': 'Norris',
        }

        user = UserFactory()
        user.email = data['email']
        user.save()

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {
            'email': [
                "An account for the specified email address already exists."
            ]
        }
        self.assertEqual(json.loads(response.content), content)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "AUTO_ACTIVATE_USER": False,
            "FRONTEND_INTEGRATION": {
                "ACTIVATION_URL": "fake_url",
            }
        }
    )
    def test_create_user_activation_email(self):
        """
        Ensure that the activation email is sent when user signs up.
        """

        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'phone': '1234567890',
            'first_name': 'Chuck',
            'last_name': 'Norris',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        # Test that one message was sent:
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [data['email']])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content)['phone'], '1234567890')

        user = User.objects.get(username="John")
        activation_token = ActionToken.objects.filter(
            user=user,
            type='account_activation',
        )

        self.assertFalse(user.is_active)
        self.assertEqual(1, len(activation_token))

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": False,
            "AUTO_ACTIVATE_USER": False,
            "FRONTEND_INTEGRATION": {
                "ACTIVATION_URL": "fake_url",
            }
        }
    )
    def test_create_user_activation_not_service_email(self):
        """
        Ensure that the user is notified that no email was sent.
        """
        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'phone': '1234567890',
            'first_name': 'Chuck',
            'last_name': 'Norris',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        # Test that one message was sent:
        self.assertEqual(len(mail.outbox), 0)

        content = {
            'detail': "The account was created but no email was sent "
                      "(email service deactivated). If your account is not activated, "
                      "contact the administration.",
        }

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), content)

        user = User.objects.get(username="John")
        activation_token = ActionToken.objects.filter(
            user=user,
            type='account_activation',
        )

        self.assertFalse(user.is_active)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "AUTO_ACTIVATE_USER": False,
            "FRONTEND_INTEGRATION": {
                "ACTIVATION_URL": "fake_url",
            }
        }
    )
    def test_create_user_activation_email_failure(self):
        """
        Ensure that the user is notified that no email was sent.
        """
        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'phone': '1234567890',
            'first_name': 'Chuck',
            'last_name': 'Norris',
        }

        @receiver(pre_send, weak=False)
        def cancel_pre_send(sender, message, esp_name, **kwargs):
            raise AnymailCancelSend("whoa there")

        self.addCleanup(pre_send.disconnect, receiver=cancel_pre_send)

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        # Test that one message was sent:
        self.assertEqual(len(mail.outbox), 0)

        content = {
            'detail': 'The account was created but no email was sent. If your account is '
                        'not activated, contact the administration.',
        }

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), content)

        user = User.objects.get(username="John")
        activation_token = ActionToken.objects.filter(
            user=user,
            type='account_activation',
        )

        self.assertFalse(user.is_active)
        self.assertEqual(1, len(activation_token))

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": False,
            "AUTO_ACTIVATE_USER": True,
            "FRONTEND_INTEGRATION": {
                "ACTIVATION_URL": "fake_url",
            }
        }
    )
    def test_create_user_auto_activate(self):
        """
        Ensure that the user is automatically activated.
        """
        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'phone': '1234567890',
            'first_name': 'Chuck',
            'last_name': 'Norris',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        content = {
            'detail': "The account was created but no email was sent "
                      "(email service deactivated). If your account is not activated, "
                      "contact the administration.",
        }

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), content)

        user = User.objects.get(username="John")

        # Test that one message wasn't sent
        self.assertEqual(len(mail.outbox), 0)

        activation_token = ActionToken.objects.filter(
            user=user,
            type='account_activation',
        )

        self.assertTrue(user.is_active)
        self.assertEqual(1, len(activation_token))

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "AUTO_ACTIVATE_USER": True,
            "FRONTEND_INTEGRATION": {
                "ACTIVATION_URL": "fake_url",
            }
        }
    )
    def test_list_users(self):
        """
        Ensure we can list all users.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse('users'))

        self.assertEqual(json.loads(response.content)['count'], 3)

        first_user = json.loads(response.content)['results'][0]
        self.assertEqual(first_user['id'], self.user.id)

        # Check the system doesn't return attributes not expected
        attributes = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'phone',
            'mobile',
            'is_superuser',
            'managed_cell',
        ]
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

    def test_list_user_as_cell_manager(self):
        self.assertEqual(self.user_cell_manager.has_perm('auth.view_user'), True)

        self.client.force_authenticate(user=self.user_cell_manager)

        response = self.client.get(reverse('users'))

        self.assertEqual(response.json()['count'], 3)
