import json

from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory
from django.urls import reverse

from api_volontaria.apps.volunteer.models import (
    Event,
    Cell,
    TaskType,
)
from api_volontaria.factories import (
    UserFactory,
    AdminFactory,
)
from api_volontaria.testClasses import CustomAPITestCase

from datetime import datetime
import pytz
from django.conf import settings
LOCAL_TIMEZONE = pytz.timezone(settings.TIME_ZONE)


class EventsTests(CustomAPITestCase):

    ATTRIBUTES = [
        'id',
        'url',
        'description',
        'start_time',
        'end_time',
        'nb_volunteers_needed',
        'nb_volunteers_standby_needed',
        'cell',
        'task_type',
        'nb_volunteers_standby',
        'nb_volunteers'
    ]

    def setUp(self):
        self.client = APIClient()

        factory = APIRequestFactory()
        self.request = factory.get('/')

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

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

    def test_create_new_event_as_admin(self):
        """
        Ensure we can create a new event if we are an admin.
        """
        data_post = {
            "description": "My new event description",
            "start_time": LOCAL_TIMEZONE.localize(datetime(2100, 1, 13, 9)),
            "end_time": LOCAL_TIMEZONE.localize(datetime(2100, 1, 15, 10)),
            "nb_volunteers_needed": 10,
            "nb_volunteers_standby_needed": 0,
            "cell": reverse(
                'cell-detail',
                args=[self.cell.id],
            ),
            "task_type": reverse(
                'tasktype-detail',
                args=[self.tasktype.id],
            )
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('event-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.check_attributes(content)

    def test_create_new_event(self):
        """
        Ensure we can't create a new event if we are a simple user.
        """
        data_post = {
            "description": "My new event description",
            "start_time": LOCAL_TIMEZONE.localize(datetime(2100, 1, 13, 9)),
            "end_time": LOCAL_TIMEZONE.localize(datetime(2100, 1, 15, 10)),
            "nb_volunteers_needed": 10,
            "nb_volunteers_standby_needed": 0,
            "cell": self.cell.id,
            "task_type": self.tasktype.id,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('event-list'),
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

    def test_update_event_as_admin(self):
        """
        Ensure we can update a event if we are an admin.
        """
        new_number_of_volunteer = 2
        data_post = {
            'nb_volunteers_needed': new_number_of_volunteer,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'event-detail',
                kwargs={
                    'pk': self.event.id
                },
            ),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_attributes(content)
        self.assertEqual(
            content['nb_volunteers_needed'],
            new_number_of_volunteer,
        )

    def test_update_event(self):
        """
        Ensure we can't update a event if we are a simple user.
        """
        new_number_of_volunteers = 2
        data_post = {
            'nb_volunteers_needed': new_number_of_volunteers,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'event-detail',
                kwargs={
                    'pk': self.event.id
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

    def test_delete_event_as_admin(self):
        """
        Ensure we can delete a event if we are an admin.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'event-detail',
                kwargs={
                    'pk': self.event.id
                },
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')

    def test_delete_event(self):
        """
        Ensure we can't delete a event if we are a simple user.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'event-detail',
                kwargs={
                    'pk': self.event.id
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

    def test_list_events(self):
        """
        Ensure we can list events.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse('event-list'),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content['results']), 1)
        self.check_attributes(content['results'][0])
