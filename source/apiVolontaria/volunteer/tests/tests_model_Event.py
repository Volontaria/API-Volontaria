from rest_framework.test import APIClient, APITransactionTestCase

from django.db import IntegrityError
from django.utils import timezone

from apiVolontaria.factories import UserFactory, AdminFactory
from location.models import Address, StateProvince, Country
from ..models import Cell, TaskType, Cycle, Event


class EventTests(APITransactionTestCase):

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

    def test_create_event(self):
        """
        Ensure we can create a new event with just required arguments
        """
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(
            minutes=100
        )

        event = Event.objects.create(
            cell=self.cell,
            cycle=self.cycle,
            task_type=self.task_type,
            start_date=start_date,
            end_date=end_date,
        )

        self.assertEqual(event.cell, self.cell)
        self.assertEqual(event.cycle, self.cycle)
        self.assertEqual(event.task_type, self.task_type)
        self.assertEqual(event.start_date, start_date)
        self.assertEqual(event.end_date, end_date)
        self.assertEqual(event.nb_volunteers_needed, 0)
        self.assertEqual(event.nb_volunteers_standby_needed, 0)

    def test_create_event_missing_cell(self):
        """
        Ensure we can't create a new event without required cell
        """
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(
            minutes=100
        )

        self.assertRaises(
            IntegrityError,
            Event.objects.create,
            cycle=self.cycle,
            task_type=self.task_type,
            start_date=start_date,
            end_date=end_date,
        )

    def test_create_event_missing_cycle(self):
        """
        Ensure we can't create a new event without required cycle
        """
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(
            minutes=100
        )

        self.assertRaises(
            IntegrityError,
            Event.objects.create,
            cell=self.cell,
            task_type=self.task_type,
            start_date=start_date,
            end_date=end_date,
        )

    def test_create_event_missing_tasktype(self):
        """
        Ensure we can't create a new event without required tasktype
        """
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(
            minutes=100
        )

        self.assertRaises(
            IntegrityError,
            Event.objects.create,
            cell=self.cell,
            cycle=self.cycle,
            start_date=start_date,
            end_date=end_date,
        )

    def test_create_event_missing_start_date(self):
        """
        Ensure we can't create a new event without required start_date
        """
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(
            minutes=100
        )

        self.assertRaises(
            IntegrityError,
            Event.objects.create,
            cell=self.cell,
            cycle=self.cycle,
            task_type=self.task_type,
            end_date=end_date,
        )

    def test_create_event_missing_end_date(self):
        """
        Ensure we can't create a new event without required end_date
        """
        start_date = timezone.now()

        self.assertRaises(
            IntegrityError,
            Event.objects.create,
            cell=self.cell,
            cycle=self.cycle,
            start_date=start_date,
            task_type=self.task_type,
        )

    def test_is_expired_property_true(self):
        """
        Ensure we have True if the event is expired
        """
        start_date = timezone.now()
        end_date = start_date

        event = Event.objects.create(
            cell=self.cell,
            cycle=self.cycle,
            task_type=self.task_type,
            start_date=start_date,
            end_date=end_date,
        )

        self.assertEqual(event.is_expired, True)

    def test_is_expired_property_false(self):
        """
        Ensure we have False if the event is not expired
        """
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(
            minutes=100
        )

        event = Event.objects.create(
            cell=self.cell,
            cycle=self.cycle,
            task_type=self.task_type,
            start_date=start_date,
            end_date=end_date,
        )

        self.assertEqual(event.is_expired, False)

    def test_is_active_property_true(self):
        """
        Ensure we have True if the event is active
        """
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(
            minutes=100,
        )

        cycle = Cycle.objects.create(
            name="my cycle",
            start_date=start_date,
            end_date=end_date,
        )

        event = Event.objects.create(
            cell=self.cell,
            cycle=cycle,
            task_type=self.task_type,
            start_date=start_date,
            end_date=end_date,
        )

        self.assertEqual(event.is_active, True)

    def test_is_active_property_false(self):
        """
        Ensure we have False if the event is not active
        """
        start_date = timezone.now()
        end_date = start_date

        cycle = Cycle.objects.create(
            name="my cycle",
            start_date=start_date,
            end_date=end_date,
        )

        event = Event.objects.create(
            cell=self.cell,
            cycle=cycle,
            task_type=self.task_type,
            start_date=start_date,
            end_date=end_date,
        )

        self.assertEqual(event.is_active, False)

    def test_create_event_with_end_date_older_than_start_date(self):
        """
        Ensure we can't create a new event with an end_date older
        than the start_date.
        """
        # Here we have an end_date older than the start_date
        end_date = timezone.now()
        start_date = end_date + timezone.timedelta(
            minutes=100,
        )

        self.assertRaises(
            IntegrityError,
            Event.objects.create,
            cell=self.cell,
            cycle=self.cycle,
            start_date=start_date,
            end_date=end_date,
            task_type=self.task_type,
        )

    def test_create_event_end_date_younger_than_end_date_of_cycle(self):
        """
        Ensure we can't create a new event with an end_date younger
        than the end_date of the cycle.
        """
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(
            minutes=100,
        )
        end_date_of_cycle = start_date + timezone.timedelta(
            minutes=10,
        )

        cycle = Cycle.objects.create(
            name="new cycle",
            start_date=start_date,
            end_date=end_date_of_cycle
        )
        self.assertRaises(
            IntegrityError,
            Event.objects.create,
            cell=self.cell,
            cycle=cycle,
            start_date=start_date,
            end_date=end_date,
            task_type=self.task_type,
        )

    def test_create_event_start_date_older_than_start_date_of_cycle(self):
        """
        Ensure we can't create a new event with a start_date older
        than the start_date of the cycle.
        """
        start_date = timezone.now()
        start_date_of_cycle = start_date + timezone.timedelta(
            minutes=10,
        )
        end_date = start_date + timezone.timedelta(
            minutes=100,
        )

        cycle = Cycle.objects.create(
            name="new cycle",
            start_date=start_date_of_cycle,
            end_date=end_date
        )
        self.assertRaises(
            IntegrityError,
            Event.objects.create,
            cell=self.cell,
            cycle=cycle,
            start_date=start_date,
            end_date=end_date,
            task_type=self.task_type,
        )
