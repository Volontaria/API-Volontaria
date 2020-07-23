import json
from datetime import datetime

from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse

from api_volontaria.apps.volunteer.models import (
    Participation,
    Cell,
    TaskType,
    Event,
)
from api_volontaria.factories import (
    UserFactory,
    AdminFactory,
)
from api_volontaria.testClasses import CustomAPITestCase

import pytz
from django.conf import settings
LOCAL_TIMEZONE = pytz.timezone(settings.TIME_ZONE)


class ParticipationsTests(CustomAPITestCase):

    ATTRIBUTES = [
        'id',
        'url',
        'event',
        'user',
        'presence_duration_minutes',
        'presence_status',
        'is_standby',
        'registered_at',
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

        self.cell = Cell.objects.create(
            name='My new cell',
            address_line_1='373 Rue villeneuve E',
            postal_code='H2T 1M1',
            city='Montreal',
            state_province='Quebec',
            longitude='45.540237',
            latitude='-73.603421',
        )

        self.tasktype = TaskType.objects.create(
            name='My new tasktype',
        )

        self.event = Event.objects.create(
            start_time=LOCAL_TIMEZONE.localize(datetime(2140, 1, 15, 8)),
            end_time=LOCAL_TIMEZONE.localize(datetime(2140, 1, 17, 12)),
            nb_volunteers_needed=10,
            nb_volunteers_standby_needed=0,
            cell=self.cell,
            task_type=self.tasktype,
        )

        self.event2 = Event.objects.create(
            start_time=LOCAL_TIMEZONE.localize(datetime(2140, 1, 15, 8)),
            end_time=LOCAL_TIMEZONE.localize(datetime(2140, 1, 17, 12)),
            nb_volunteers_needed=10,
            nb_volunteers_standby_needed=0,
            cell=self.cell,
            task_type=self.tasktype,
        )

        self.participation = Participation.objects.create(
            event=self.event2,
            user=self.user,
            is_standby=False,
        )

        self.participation2 = Participation.objects.create(
            event=self.event2,
            user=self.user2,
            is_standby=False,
        )

    def test_create_new_participation_as_admin(self):
        """
        Ensure we can create a new participation if we are an admin.
        """
        data_post = {
            'event': reverse(
                'event-detail',
                args=[self.event.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.admin.id],
            ),
            'is_standby': False,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('participation-list'),
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

    def test_create_new_participation(self):
        """
        Ensure we can create a new participation if we are a simple user.
        """
        data_post = {
            'event': reverse(
                'event-detail',
                args=[self.event.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user.id],
            ),
            'is_standby': False,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('participation-list'),
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

    def test_create_new_participation_for_an_other_user(self):
        """
        Ensure we can't create a new participation for an other user
        if we are a simple user.
        """
        data_post = {
            'event': reverse(
                'event-detail',
                args=[self.event.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user2.id],
            ),
            'is_standby': False,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('participation-list'),
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
                    "You don't have the right to create a participation "
                    "for an other user"
                ]
            }
        )

    def test_create_new_participation_for_an_other_user_as_admin(self):
        """
        Ensure we can create a new participation for an other user
        if we are an administrator.
        """
        data_post = {
            'event': reverse(
                'event-detail',
                args=[self.event.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user2.id],
            ),
            'is_standby': False,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('participation-list'),
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

    def test_update_participation_as_admin(self):
        """
        Ensure we can update a participation if we are an admin.
        """
        new_value = True
        data_post = {
            'is_standby': new_value,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'participation-detail',
                kwargs={
                    'pk': self.participation.id
                },
            ),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_attributes(content)
        self.assertEqual(content['is_standby'], new_value)

    def test_update_participation(self):
        """
        Ensure we can't update a participation if we are a simple user.
        """
        new_value = True
        data_post = {
            'is_standby': new_value,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'participation-detail',
                kwargs={
                    'pk': self.participation.id
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

    def test_delete_participation_as_admin(self):
        """
        Ensure we can delete a participation if we are an admin.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'participation-detail',
                kwargs={
                    'pk': self.participation.id
                },
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')

    def test_delete_participation(self):
        """
        Ensure we can't delete a participation if we are a simple user.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'participation-detail',
                kwargs={
                    'pk': self.participation.id
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

    def test_list_participations(self):
        """
        Ensure we can list participations.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse('participation-list'),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content['results']), 1)
        self.check_attributes(content['results'][0])

        for participation in content['results']:
            self.assertEqual(
               participation['user']['id'],
               self.user.id,
            )

    def test_list_participations_as_admin(self):
        """
        Ensure we can list all the participations where we are administrator
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse('participation-list'),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content['results']), 2)
        self.check_attributes(content['results'][0])

        at_least_one_participation_is_owner_by_somebody_else = False
        for participation in content['results']:
            if participation['user']['id'] != self.admin.id:
                at_least_one_participation_is_owner_by_somebody_else = True

        self.assertTrue(at_least_one_participation_is_owner_by_somebody_else)
