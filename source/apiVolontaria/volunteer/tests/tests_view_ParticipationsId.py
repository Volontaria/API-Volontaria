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

        self.user_cell_manager = UserFactory()
        self.user_cell_manager.set_password('Test123!')

        self.user_cell_manager_no_perms = UserFactory()
        self.user_cell_manager_no_perms.set_password('Test123!')
        self.user_cell_manager_no_perms.save()

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
        self.cell_with_manager = Cell.objects.create(
            name="my cell with manager",
            address=self.address,
        )

        self.cell_with_manager.managers.set([self.user_cell_manager])
        self.cell_with_manager.save()

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

        self.event_with_manager = Event.objects.create(
            cell=self.cell_with_manager,
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

            self.participation_cell_manager = Participation.objects.create(
                standby=True,
                subscription_date=subscription_date,
                user=self.user2,
                event=self.event_with_manager,
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

    def test_retrieve_participation_as_owner(self):
        """
        Ensure we can retrieve a participation as the owner.
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

    def test_retrieve_participation_basic_serializer(self):
        """
        Ensure we can retrieve a participation.
        Using the BasicSerializer
        """

        subscription_date_str = self.participation2.subscription_date.\
            strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        duration_minutes = self.participation2.presence_duration_minutes
        data = dict(
            id=self.participation2.id,
            standby=self.participation2.standby,
            subscription_date=subscription_date_str,
            event=self.participation2.event.id,
            presence_duration_minutes=duration_minutes,
            presence_status=self.participation2.presence_status,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'volunteer:participations_id',
                kwargs={'pk': self.participation2.id},
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

    def test_update_participation_cell_manager(self):
        """
        Ensure we have the right to modify a Participation
        if the user is a Cell manager
        """
        self.client.force_authenticate(user=self.user_cell_manager)

        data_patch = {'presence_status': 'P'}

        subscription_date = timezone.now()

        subscription_date_str = subscription_date.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ",
        )

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = subscription_date
            response = self.client.patch(
                reverse(
                    'volunteer:participations_id',
                    kwargs={'pk': self.participation_cell_manager.id}
                ),
                data_patch,
                format='json',
            )

        content = {
            "id": self.participation_cell_manager.id,
            "event": self.participation_cell_manager.event.pk,
            "user": {
                "id": self.user2.id,
                "username": self.user2.username,
                "email": self.user2.email,
                "first_name": self.user2.first_name,
                "last_name": self.user2.last_name,
                "is_active": self.user2.is_active,
                "is_superuser": self.user2.is_superuser,
                "phone": None,
                "mobile": None,
                "managed_cell": []
            },
            "standby": True,
            "subscription_date": subscription_date_str,
            "presence_duration_minutes": None,
            "presence_status": "P"
        }

        self.assertEqual(json.loads(response.content), content)

    def test_update_participation_cell_manager_no_perms(self):
        """
        Ensure we don't have the right to modify a Participation
        if the user is not a Cell manager
        """
        self.client.force_authenticate(user=self.user_cell_manager_no_perms)

        data_patch = {'presence_status': 'P'}

        subscription_date = timezone.now()

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = subscription_date
            response = self.client.patch(
                reverse(
                    'volunteer:participations_id',
                    kwargs={'pk': self.participation_cell_manager.id}
                ),
                data_patch,
                format='json',
            )

        content = {
            'detail': "You do not have permission to perform this action.",
        }

        self.assertEqual(json.loads(response.content), content)

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
            'non_field_errors':
                "You can't delete a participation if the "
                "associated event is already started",
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_participation_event_started_admin(self):
        """
        Ensure we can't delete a specific participation if
        the event is already started.
        """
        self.client.force_authenticate(user=self.admin)

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

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_participation_event_started_cell_manager(self):
        """
        Ensure we can't delete a specific participation if
        the event is already started.
        """
        self.client.force_authenticate(user=self.user_cell_manager)

        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(
            minutes=100,
        )

        event = Event.objects.create(
            cell=self.cell_with_manager,
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

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

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
