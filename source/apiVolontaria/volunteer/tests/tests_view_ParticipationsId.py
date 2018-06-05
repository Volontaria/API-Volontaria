import json

from unittest import mock

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import Permission

from apiVolontaria.factories import UserFactory, AdminFactory
from location.models import Address, StateProvince, Country
from ..models import Cell, Event, Cycle, TaskType, Participation


class ParticipationsIdTests(APITestCase):

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
        self.cycle = Cycle.objects.create(
            name="my cycle",
        )
        self.task_type = TaskType.objects.create(
            name="my tasktype",
        )

        start_date = timezone.now() + timezone.timedelta(
            minutes=100,
        )
        end_date = start_date + timezone.timedelta(
            minutes=100,
        )

        self.event = Event.objects.create(
            cell=self.cell,
            cycle=self.cycle,
            task_type=self.task_type,
            start_date=start_date,
            end_date=end_date,
        )

        self.event2 = Event.objects.create(
            cell=self.cell,
            cycle=self.cycle,
            task_type=self.task_type,
            start_date=start_date,
            end_date=end_date,
        )

        subscription_date = timezone.now()

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = subscription_date
            self.participation = Participation.objects.create(
                standby=True,
                subscription_date=subscription_date,
                user=self.user,
                event=self.event2,
            )

            self.participation2 = Participation.objects.create(
                standby=True,
                subscription_date=subscription_date,
                user=self.user2,
                event=self.event2,
            )

    def test_retrieve_participation_id_not_exist(self):
        """
        Ensure we can't retrieve a participation that doesn't exist.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'volunteer:participations_id',
                kwargs={'pk': 999},
            ),
            format='json',
        )

        content = {"detail": "Not found."}

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), content)

    def test_retrieve_participation(self):
        """
        Ensure we can retrieve a participation.
        """

        subscription_date_str = self.participation.subscription_date.\
            strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        duration_minutes = self.participation.presence_duration_minutes
        data = dict(
            id=self.participation.id,
            standby=self.participation.standby,
            subscription_date=subscription_date_str,
            event=self.participation.event.id,
            presence_duration_minutes=duration_minutes,
            presence_status=self.participation.presence_status,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'volunteer:participations_id',
                kwargs={'pk': self.participation.id},
            )
        )

        content = json.loads(response.content)
        del content['user']
        self.assertEqual(content, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_participation_with_permission(self):
        """
        Ensure we can update a specific participation if the caller owns it.
        """
        subscription_date = timezone.now()

        subscription_date_str = subscription_date.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

        duration_minutes = self.participation.presence_duration_minutes
        data = dict(
            id=self.participation.id,
            standby=False,
            subscription_date=subscription_date_str,
            event=self.participation.event.id,
            presence_duration_minutes=duration_minutes,
            presence_status=self.participation.presence_status,
        )

        data_post = {
            "standby": False,
        }

        self.client.force_authenticate(user=self.user)

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = subscription_date
            response = self.client.patch(
                reverse(
                    'volunteer:participations_id',
                    kwargs={'pk': self.participation.id},
                ),
                data_post,
                format='json',
            )

        content = json.loads(response.content)
        del content['user']
        self.assertEqual(content, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_participation_with_superuser(self):
        """
        Ensure we can update a specific participation if we are superuser.
        """
        subscription_date = timezone.now()

        subscription_date_str = subscription_date.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ",
        )

        data = dict(
            id=self.participation.id,
            standby=self.participation.standby,
            subscription_date=subscription_date_str,
            event=self.participation.event.id,
            presence_duration_minutes=14,
            presence_status='P',
        )

        data_post = {
            "presence_status": 'P',
            "presence_duration_minutes": 14,
        }

        self.client.force_authenticate(user=self.admin)

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = subscription_date
            response = self.client.patch(
                reverse(
                    'volunteer:participations_id',
                    kwargs={'pk': self.participation.id},
                ),
                data_post,
                format='json',
            )

        content = json.loads(response.content)
        del content['user']
        self.assertEqual(content, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_participation_status(self):
        """
        Ensure we can update our own participation status if we're user.
        """
        subscription_date = timezone.now()

        subscription_date_str = subscription_date.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ",
        )

        duration_minutes = self.participation.presence_duration_minutes
        data = dict(
            id=self.participation.id,
            standby=self.participation.standby,
            subscription_date=subscription_date_str,
            event=self.participation.event.id,
            presence_duration_minutes=duration_minutes,
            presence_status=self.participation.presence_status,
        )

        data_post = {
            "presence_status": 'P',
            "presence_duration_minutes": 14,
        }

        self.client.force_authenticate(user=self.user)

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = subscription_date
            response = self.client.patch(
                reverse(
                    'volunteer:participations_id',
                    kwargs={'pk': self.participation.id},
                ),
                data_post,
                format='json',
            )

        content = json.loads(response.content)
        del content['user']
        self.assertEqual(content, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_participation_without_permission(self):
        """
        Ensure we can't update a specific participation of another user.
        """
        data_post = {
            "standby": False,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'volunteer:participations_id',
                kwargs={'pk': self.participation2.id},
            ),
            data_post,
            format='json',
        )

        content = {
            'detail': "You do not have permission to perform this action.",
        }
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_participation_that_doesnt_exist(self):
        """
        Ensure we can't update a specific participation if it doesn't exist.
        """
        data_post = {
            "standby": True,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'volunteer:participations_id',
                kwargs={'pk': 9999},
            ),
            data_post,
            format='json',
        )

        content = {'detail': "Not found."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_participation_with_permission(self):
        """
        Ensure we can delete a specific participation if the caller owns it.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            reverse(
                'volunteer:participations_id',
                kwargs={'pk': self.participation.id},
            ),
        )

        self.assertEqual(response.content, b'')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_participation_but_event_already_started(self):
        """
        Ensure we can't delete a specific participation if
        the event is already started.
        """
        self.client.force_authenticate(user=self.user)

        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(
            minutes=100,
        )

        event = Event.objects.create(
            cell=self.cell,
            cycle=self.cycle,
            task_type=self.task_type,
            start_date=start_date,
            end_date=end_date,
        )

        participation = Participation.objects.create(
            standby=True,
            user=self.user,
            event=event,
        )

        response = self.client.delete(
            reverse(
                'volunteer:participations_id',
                kwargs={'pk': participation.id},
            ),
        )

        content = {
            'non_field_errors': "You can't delete a participation if the "
                      "associated event is already started",
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_participation_without_permission(self):
        """
        Ensure we can't delete a specific participation without owning it.
        """

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            reverse(
                'volunteer:participations_id',
                kwargs={'pk': self.participation2.id},
            ),
        )

        content = {
            'detail': "You do not have permission to perform this action.",
        }
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_participation_that_doesnt_exist(self):
        """
        Ensure we can't delete a specific participation if it doesn't exist
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            reverse(
                'volunteer:participations_id',
                kwargs={'pk': 9999},
            ),
        )

        content = {'detail': "Not found."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
