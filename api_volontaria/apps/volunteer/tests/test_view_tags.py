import json

from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory
from django.urls import reverse

from api_volontaria.apps.volunteer.models import (
    Event,
    Cell,
    TaskType,
    Tag)
from api_volontaria.factories import (
    UserFactory,
    AdminFactory,
)
from api_volontaria.testClasses import CustomAPITestCase

from datetime import datetime
import pytz
from django.conf import settings
LOCAL_TIMEZONE = pytz.timezone(settings.TIME_ZONE)


class TagsTests(CustomAPITestCase):

    ATTRIBUTES = [
        'id',
        'url',
        'name',
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

        self.tag = Tag.objects.create(
            name='My Tag',
        )

        self.event = Event.objects.create(
            start_time=LOCAL_TIMEZONE.localize(datetime(2140, 1, 15, 8)),
            end_time=LOCAL_TIMEZONE.localize(datetime(2140, 1, 17, 12)),
            nb_volunteers_needed=10,
            nb_volunteers_standby_needed=0,
            cell=self.cell,
            task_type=self.tasktype,
        )

    def test_create_new_tag_as_admin(self):
        """
        Ensure we can create a new tag if we are an admin.
        """
        data_post = {
            "name": 'My Tag Test',
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('tag-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.check_attributes(content)

    def test_create_new_tag(self):
        """
        Ensure we can't create a new tag if we are a simple user.
        """
        data_post = {
            "name": 'My Tag Test',
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('tag-list'),
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

    def test_update_tag_as_admin(self):
        """
        Ensure we can update a tag if we are an admin.
        """
        data_post = {
            'name': 'New tag Name',
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'tag-detail',
                kwargs={
                    'pk': self.tag.id
                },
            ),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_attributes(content)

    def test_update_tag(self):
        """
        Ensure we can't update a tag if we are a simple user.
        """
        data_post = {
            'name': 'New tag Name',
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'tag-detail',
                kwargs={
                    'pk': self.tag.id
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

    def test_delete_tag_as_admin(self):
        """
        Ensure we can delete a tag if we are an admin.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'tag-detail',
                kwargs={
                    'pk': self.tag.id
                },
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')

    def test_delete_tag(self):
        """
        Ensure we can't delete a tag if we are a simple user.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'tag-detail',
                kwargs={
                    'pk': self.tag.id
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

    def test_list_tags(self):
        """
        Ensure we can list tags.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse('tag-list'),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content['results']), 1)
        self.check_attributes(content['results'][0])
