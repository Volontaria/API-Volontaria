from unittest import mock

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from apiVolontaria.factories import UserFactory
from location.models import Address, StateProvince, Country
from volunteer.models import Participation, Event, Cycle, Cell, TaskType
from volunteer.resources import ParticipationResource


class ParticipationsTests(APITestCase):
    def setUp(self):

        user = User.objects.create_user('admin', 'admin@example.com',
                                        'password')
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.client.login(username='admin', password='password')

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.user2 = UserFactory()
        self.user2.set_password('Test123!')
        self.user2.save()

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

        start_date = timezone.now() - timezone.timedelta(
            minutes=100,
        )
        end_date = start_date + timezone.timedelta(
            minutes=50,
        )

        self.cycle_inactive = Cycle.objects.create(
            name="my cycle",
            start_date=start_date,
            end_date=end_date,
        )

        # Some date INSIDE the cycle range
        start_date = start_date + timezone.timedelta(
            minutes=1,
        )
        end_date = end_date - timezone.timedelta(
            minutes=1,
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
                user=self.user,
                event=self.event2,
            )

            self.participation2 = Participation.objects.create(
                standby=True,
                user=self.user2,
                event=self.event2,
            )

        self.dataset = ParticipationResource().export()

    def test_exportation_header(self):
        csv_header = "standby,first_name,last_name,email,phone," \
                     "mobile,event__start_date,event__end_date,cell"
        self.assertNotIn(self.dataset.csv, csv_header)

    def test_export(self):
        data = {
            'action': ['export_admin_action'],
            'file_format': '0',
            '_selected_action': [str(self.participation.id)],
        }
        response = self.client.post('/admin/volunteer/participation/', data)

        self.assertContains(
            response, self.participation.user.email, status_code=200
        )
        self.assertNotContains(
            response, self.participation2.user.email, status_code=200
        )
        self.assertTrue(response.has_header("Content-Disposition"))

    def test_export_no_format_selected(self):
        data = {
            'action': ['export_admin_action'],
            '_selected_action': [str(self.participation.id)],
        }
        response = self.client.post('/admin/volunteer/participation/', data)
        self.assertEqual(response.status_code, 302)
