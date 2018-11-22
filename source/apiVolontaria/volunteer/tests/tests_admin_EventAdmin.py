import datetime
from django.contrib.auth.models import User
from rest_framework.test import APITransactionTestCase

from django.contrib.admin.sites import AdminSite
from django.test import Client

from apiVolontaria.models import Profile
from location.models import Address, StateProvince, Country
from volunteer.forms import EventAdminForm
from ..admin import EventAdmin
from ..models import Event, Cycle, Cell, TaskType


class EventAdminTests(APITransactionTestCase):

    def setUp(self):
        self.create_user()

        self.site = AdminSite()
        self.admin = EventAdmin(Event, self.site)

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

        self.task_type = TaskType.objects.create(
            name="my tasktype",
        )

        self.cycle = Cycle.objects.create(
            name="my cycle",
            start_date=datetime.datetime(2018, 11, 15, 00, 00, 00),
            end_date=datetime.datetime(2018, 11, 17, 00, 00, 00),
        )

    def create_user(self):
        self.username = "test_admin"
        self.password = User.objects.make_random_password()
        user, created = User.objects.get_or_create(username=self.username)
        user.set_password(self.password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        self.user = user

        profile = Profile(
            user=user,
            phone='1234567890',
            mobile='0987654321'
        )

        profile.save()

    def test_admin_access(self):
        client = Client()
        client.login(username=self.username, password=self.password)

        admin_pages = [
            "/admin/volunteer/",
            "/admin/volunteer/event/",
            ]

        for page in admin_pages:
            resp = client.get(page)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!DOCTYPE html", str(resp.content))

    def test_admin_events(self):
        self.assertNotEqual(self.admin, None)

    def test_admin_form_dates(self):
        data_wrong_start_end_date = {
            'start_date': datetime.datetime(2018, 11, 23, 00, 00, 00),
            'end_date': datetime.datetime(2018, 11, 22, 00, 00, 00)
        }
        form = EventAdminForm(data_wrong_start_end_date)

        form.is_valid()

        self.assertEqual(form.errors['start_date'], ['The start date needs to be older than end date.'])
        self.assertEqual(form.errors['end_date'], ['The start date needs to be older than end date.'])

        data_start_time_outside_cycle_time = {
            'start_date': datetime.datetime(2018, 11, 14, 00, 00, 00),
            'end_date': datetime.datetime(2018, 11, 18, 00, 00, 00),
            'nb_volunteers_needed': 1,
            'nb_volunteers_standby_needed': 1,
            'cell': self.cell.pk,
            'cycle': self.cycle.pk,
            'task_type': self.task_type.pk,

        }
        form = EventAdminForm(data_start_time_outside_cycle_time)

        form.is_valid()

        self.assertEqual(
            form.errors['start_date'],
            ["The start date can't be older than start date of the cycle."])

        data_end_time_outside_cycle_time = {
            'start_date': datetime.datetime(2018, 11, 16, 00, 00, 00),
            'end_date': datetime.datetime(2018, 11, 18, 00, 00, 00),
            'nb_volunteers_needed': 1,
            'nb_volunteers_standby_needed': 1,
            'cell': self.cell.pk,
            'cycle': self.cycle.pk,
            'task_type': self.task_type.pk,

        }
        form = EventAdminForm(data_end_time_outside_cycle_time)

        form.is_valid()

        self.assertEqual(
            form.errors['end_date'],
            ["The end date can't be younger than end date of the cycle."])

        data_no_cycle = {
            'start_date': datetime.datetime(2018, 11, 16, 2, 00, 00),
            'end_date': datetime.datetime(2018, 11, 16, 4, 00, 00),
            'nb_volunteers_needed': 1,
            'nb_volunteers_standby_needed': 1,
            'cell': self.cell.pk,
            'task_type': self.task_type.pk,

        }
        form = EventAdminForm(data_no_cycle)

        form.is_valid()

        self.assertEqual(
            form.errors['cycle'],
            ["This field is required."])

        data_good = {
            'start_date': datetime.datetime(2018, 11, 16, 2, 00, 00),
            'end_date': datetime.datetime(2018, 11, 16, 4, 00, 00),
            'nb_volunteers_needed': 1,
            'nb_volunteers_standby_needed': 1,
            'cell': self.cell.pk,
            'cycle': self.cycle.pk,
            'task_type': self.task_type.pk,

        }
        form = EventAdminForm(data_good)

        self.assertTrue(form.is_valid())
