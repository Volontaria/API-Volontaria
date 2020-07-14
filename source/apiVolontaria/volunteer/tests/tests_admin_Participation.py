from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITransactionTestCase

from django.contrib.admin.sites import AdminSite
from django.test import Client

from apiVolontaria.models import Profile
from location.models import Country, StateProvince, Address
from volunteer.admin import ParticipationAdmin
from volunteer.models import Participation, Cell, Cycle, TaskType, Event


class ParticipationTests(APITransactionTestCase):

    def setUp(self):
        self.create_user()

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

        self.participation = Participation(event=self.event, user=self.user)

        self.site = AdminSite()
        self.admin = ParticipationAdmin(Participation, self.site)

        self.profile = Profile.objects.filter(
            user__pk=self.participation.user.pk
        ).first()

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
            "/admin/volunteer/participation/",
            ]

        for page in admin_pages:
            resp = client.get(page)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!DOCTYPE html", str(resp.content))

    def test_admin_participations(self):
        self.assertNotEqual(self.admin, None)

    def test_admin_user_email(self):
        self.assertEqual(self.admin.user__email(self.participation),
                         self.participation.user.email)

    def test_admin_user_first_name(self):
        self.assertEqual(self.admin.user__first_name(self.participation),
                         self.participation.user.first_name)

    def test_admin_user_last_name(self):
        self.assertEqual(self.admin.user__last_name(self.participation),
                         self.participation.user.last_name)

    def test_admin_user_phone(self):
        self.assertEqual(
            self.admin.user__phone(self.participation),
            self.profile.phone
        )

    def test_admin_user_mobile(self):
        self.assertEqual(
            self.admin.user__mobile(self.participation),
            self.profile.mobile
        )

    def test_admin_events_duration(self):
        duration = self.admin.event__duration(self.participation)
        self.assertEqual(duration, timedelta(0, 2880))
