from datetime import timedelta
from unittest import mock

from decimal import Decimal
from rest_framework.test import APIClient, APITransactionTestCase

from django.db import IntegrityError
from django.utils import timezone

from apiVolontaria.factories import UserFactory, AdminFactory
from location.models import Address, StateProvince, Country
from ..models import Cell, TaskType, Cycle, Event, Participation


class ParticipationTests(APITransactionTestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

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

        event_start_date = timezone.now()
        self.event = Event.objects.create(
            cell=self.cell,
            cycle=self.cycle,
            task_type=self.task_type,
            start_date=event_start_date,
            end_date=event_start_date + timezone.timedelta(minutes=100),
        )

        self.participation = Participation.objects.create(
            standby=True,
            user=self.admin,
            event=self.event,
        )

        self.event_2 = Event.objects.create(
            cell=self.cell,
            cycle=self.cycle,
            task_type=self.task_type,
            start_date=event_start_date,
            end_date=event_start_date + timezone.timedelta(minutes=100),
        )

        self.participation_presence = Participation.objects.create(
            standby=True,
            user=self.admin,
            event=self.event_2,
            presence_status='P',
            presence_duration_minutes=300,
        )

    def test_create_participation(self):
        """
        Ensure we can create a new participation with just required arguments
        """

        subscription_date = timezone.now()

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = subscription_date
            participation = Participation.objects.create(
                standby=True,
                user=self.user,
                event=self.event,
            )

        self.assertEqual(participation.standby, True)
        self.assertEqual(participation.subscription_date, subscription_date)
        self.assertEqual(participation.user.id, self.user.id)
        self.assertEqual(participation.event.id, self.event.id)

    def test_create_participation_missing_event(self):
        """
        Ensure we can't create a new participation without required event
        """
        subscription_date = timezone.now()

        self.assertRaises(
            IntegrityError,
            Participation.objects.create,
            standby=True,
            subscription_date=subscription_date,
            user=self.user,
        )

    def test_create_participation_missing_user(self):
        """
        Ensure we can't create a new participation without required user
        """
        subscription_date = timezone.now()

        self.assertRaises(
            IntegrityError,
            Participation.objects.create,
            standby=True,
            subscription_date=subscription_date,
            event=self.event,
        )

    def test_create_participation_missing_standby(self):
        """
        Ensure we can't create a new participation without required standby
        """
        subscription_date = timezone.now()

        self.assertRaises(
            IntegrityError,
            Participation.objects.create,
            subscription_date=subscription_date,
            user=self.user,
            event=self.event,
        )

    def test_start_date_property(self):
        """
        Check start_date property
        """

        self.assertEqual(
            self.participation.start_date,
            self.participation.event.start_date
        )

    def test_end_date_property(self):
        """
        Check end_date property
        """

        self.assertEqual(
            self.participation.end_date,
            self.participation.event.end_date
        )

    def test_cell_property(self):
        """
        Check cell property
        """

        self.assertEqual(
            self.participation.cell,
            self.participation.event.cell.name
        )

    def test_duration_from_model(self):
        """
        Check duration
        """

        self.assertEqual(
            self.participation_presence.duration,
            timedelta(minutes=300)
        )

    def test_duration_from_event_property(self):
        """
        Check duration
        """
        self.assertEqual(self.participation.duration, timedelta(0, 6000))

    def test_name(self):
        self.assertIsNot(self.participation.__str__, None)
