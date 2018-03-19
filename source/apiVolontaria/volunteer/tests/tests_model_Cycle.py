from rest_framework.test import APITestCase

from apiVolontaria.factories import AdminFactory, UserFactory
from location.models import Address, StateProvince, Country
from volunteer.models import Cycle, Participation, TaskType, Event, Cell
from django.utils import timezone


class CycleTests(APITestCase):

    def setUp(self):
        pass

    def test_create_cycle(self):
        """
        Ensure we can create a new cycle with just required arguments
        """
        cycle = Cycle.objects.create(
            name='my cycle'
        )

        self.assertEquals(cycle.name, 'my cycle')

    def test_is_active_property_true(self):
        """
        Ensure we have True if the cycle is active
        """
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(
            minutes=100,
        )

        cycle = Cycle.objects.create(
            name='my cycle',
            start_date=start_date,
            end_date=end_date,
        )

        start_date += timezone.timedelta(days=1)
        end_date += timezone.timedelta(days=1)

        cycle_2 = Cycle.objects.create(
            name='my cycle',
            start_date=start_date,
            end_date=end_date,
        )

        # Event in progress
        self.assertEqual(cycle.is_active, True)
        # Event to come
        self.assertEqual(cycle_2.is_active, True)

    def test_is_active_property_false(self):
        """
        Ensure we have False if the cycle is not active
        """
        start_date = timezone.now()
        end_date = start_date

        cycle = Cycle.objects.create(
            name='my cycle',
            start_date=start_date,
            end_date=end_date,
        )

        # Event has ended
        self.assertEqual(cycle.is_active, False)

    def test_str_method(self):
        """
        Validate the string representation of cycles
        """
        start_date = timezone.now()
        end_date = start_date

        cycle = Cycle.objects.create(
            name='my cycle',
            start_date=start_date,
            end_date=end_date,
        )

        self.assertEqual(str(cycle), cycle.name)

    def test_cycle_generate_report_data_error(self):
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

        # Test error case
        test_data_error = {
            'error':
                'All of the Participations presence '
                'status must be initialised.',
        }

        data = self.cycle.generate_participation_report_data()

        self.assertEqual(data, test_data_error)

        # Test normal case
        self.participation.presence_status = 'A'
        self.participation.save()

        data = self.cycle.generate_participation_report_data()

        test_data = {
            2: {
                'first_name': self.admin.first_name,
                'last_name': self.admin.last_name,
                'email': self.admin.email,
                'total_time': 300,
            }
        }

        self.assertEqual(data, test_data)
