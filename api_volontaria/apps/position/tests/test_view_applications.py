import json
from datetime import datetime

from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse

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


class ApplicationsTests(CustomAPITestCase):

    ATTRIBUTES = [
        'id',
        'url',
        'position',
        'user',
        'applied_on',
        'motivation',
        'application_status',
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
            hourly_wage=14,
            hourly_wage_currency='CAD',
            weekly_hours=15,
            minimum_days_commitment=3,
            is_remote_job=True,
            is_posted=True,
        )

        self.position2 = Position.objects.create(
            hourly_wage=14.5,
            hourly_wage_currency='CAD',
            weekly_hours=30.5,
            minimum_days_commitment=6.5,
            is_remote_job=False,
            is_posted=False,
        )

        self.application = Application.objects.create(
            position=self.position,
            user=self.user,
            applied_on=LOCAL_TIMEZONE.localize(datetime(2022, 4, 15, 19)),
            motivation='passionate about that stuff',
            application_status=Application.APPLICATION_ACCEPTED,
        )

        self.application2 = Application.objects.create(
            position=self.position,
            user=self.user2,
            applied_on=LOCAL_TIMEZONE.localize(datetime(2023, 1, 15, 8)),
            motivation='cool mission',
            application_status=Application.APPLICATION_PENDING,
        )

        self.user_pending_application = Application.objects.create(
            position=self.position,
            user=self.user,
            applied_on=LOCAL_TIMEZONE.localize(datetime(2022, 4, 15, 19)),
            motivation='passionate about that stuff',
            application_status=Application.APPLICATION_PENDING,
        )

    def test_create_new_application_as_admin(self):
        """
        Ensure we can create a new application if we are an admin.
        """
        data_post = {
            'position': reverse(
                'position-detail',
                args=[self.position.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.admin.id],
            ),
            'motivation': 'seems fun',
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('application-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            content
        )
        self.check_attributes(content)

    def test_create_new_application(self):
        """
        Ensure we can create a new application if we are a simple user.
        """
        data_post = {
            'position': reverse(
                'position-detail',
                args=[self.position.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user.id],
            ),
            'motivation': 'seems fun',
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('application-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            content
        )
        self.check_attributes(content)

    def test_create_new_application_without_auth(self):
        """
        Ensure we can't create a new application if we are not logged in.
        """
        data_post = {
            'position': reverse(
                'position-detail',
                args=[self.position.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user.id],
            ),
            'motivation': 'seems fun',
        }

        response = self.client.post(
            reverse('application-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            content
        )

    def test_create_new_application_for_an_other_user(self):
        """
        Ensure we can't create a new application for an other user
        if we are a simple user.
        """
        data_post = {
            'position': reverse(
                'position-detail',
                args=[self.position.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user2.id],
            ),
            'motivation': 'seems fun',
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('application-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            content
        )
        self.assertEqual(
            content,
            {
                'user': [
                    "You don't have the right to create an application "
                    "for an other user"
                ]
            }
        )

    def test_create_new_application_for_an_other_user_as_admin(self):
        """
        Ensure we can create a new application for an other user
        if we are an administrator.
        """
        data_post = {
            'position': reverse(
                'position-detail',
                args=[self.position.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user2.id],
            ),
            'motivation': 'seems fun',
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('application-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            content
        )
        self.check_attributes(content)

    def test_update_application_as_admin(self):
        """
        Ensure we can update an application if we are an admin.
        """
        new_value = 'sounds great'
        data_post = {
            'motivation': new_value,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'application-detail',
                kwargs={
                    'pk': self.application.id
                },
            ),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_attributes(content)
        self.assertEqual(content['motivation'], new_value)

    def test_update_pending_application(self):
        """
        Ensure a simple user can update their own application
        as long as the application is still pending.
        """

        new_value = 'sounds great'
        data_post = {
            'motivation': new_value,
        }

        self.client.force_authenticate(user=self.user)

        self.assertEqual(
            self.user.id,
            self.user_pending_application.user.id,
        )
        self.assertEqual(
            self.user_pending_application.application_status,
            Application.APPLICATION_PENDING,
        )

        response = self.client.patch(
            reverse(
                'application-detail',
                kwargs={
                    'pk': self.user_pending_application.id,
                },
            ),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_attributes(content)
        self.assertEqual(content['motivation'], new_value)

    def test_update_non_pending_application(self):
        """
        Ensure a simple user cannot update their own application
        once the application has been either accepted or rejected.
        """
        new_value = 'sounds great'
        data_post = {
            'motivation': new_value,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'application-detail',
                kwargs={
                    'pk': self.application.id
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

    def test_update_pending_application_without_auth(self):
        """
        Ensure an unauthorized user can't update an application.
        """
        new_value = 'sounds great'
        data_post = {
            'motivation': new_value,
        }

        response = self.client.patch(
            reverse(
                'application-detail',
                kwargs={
                    'pk': self.user_pending_application.id,
                },
            ),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_application_as_admin(self):
        """
        Ensure we can delete an application if we are an admin.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'application-detail',
                kwargs={
                    'pk': self.application.id
                },
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')

    def test_delete_pending_application(self):
        """
        Ensure a simple user can delete their own application
        as long as it is still pending.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            reverse(
                'application-detail',
                kwargs={
                    'pk': self.user_pending_application.id
                },
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')

    def test_delete_non_pending_application(self):
        """
        Ensure a simple user cannot delete their own application
        once the application has been either accepted or rejected.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            reverse(
                'application-detail',
                kwargs={
                    'pk': self.application.id
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

    def test_delete_pending_application_without_auth(self):
        """
        Ensure an unauthorized user can't delete an application.
        """
        response = self.client.delete(
            reverse(
                'application-detail',
                kwargs={
                    'pk': self.user_pending_application.id
                },
            )
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_applications(self):
        """
        Ensure any user can list applications.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse('application-list'),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content['results']), 2)
        self.check_attributes(content['results'][0])

    def test_list_applications_as_admin(self):
        """
        Ensure we can list all the applications where we are administrator
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse('application-list'),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content['results']), 3)
        self.check_attributes(content['results'][0])

        at_least_one_application_is_owned_by_somebody_else = False
        for application in content['results']:
            if application['user']['id'] != self.admin.id:
                at_least_one_application_is_owned_by_somebody_else = True

        self.assertTrue(at_least_one_application_is_owned_by_somebody_else)

    def test_list_applications_without_auth(self):
        """
        Ensure any unauthorized user can't list applications.
        """
        response = self.client.get(
            reverse('application-list'),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
