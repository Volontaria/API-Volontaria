from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib.admin import ACTION_CHECKBOX_NAME
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITransactionTestCase

from django.contrib.admin.sites import AdminSite
from django.test import Client

from apiVolontaria.models import Profile
from location.models import Country, StateProvince, Address
from ..admin import CycleAdmin
from ..models import Participation, Cell, Cycle, TaskType, Event


class ParticipationTests(APITransactionTestCase):

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
            mobile='0987654321',
        )

        profile.save()

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

        self.start_date = timezone.now() - timezone.timedelta(
            minutes=100,
        )
        self.end_date = self.start_date + timezone.timedelta(
            minutes=50,
        )

        self.cycle_inactive = Cycle.objects.create(
            name="my cycle",
            start_date=self.start_date,
            end_date=self.end_date,
        )

        # Some date INSIDE the cycle range
        self.start_date = self.start_date + timezone.timedelta(
            minutes=1,
        )
        self.end_date = self.end_date - timezone.timedelta(
            minutes=1,
        )

        self.event = Event.objects.create(
            cell=self.cell,
            cycle=self.cycle,
            task_type=self.task_type,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        self.event2 = Event.objects.create(
            cell=self.cell,
            cycle=self.cycle,
            task_type=self.task_type,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        self.participation = Participation(
            event=self.event,
            user=self.user,
            standby=False,
            presence_status='P',
        )
        self.participation.save()

        self.participation2 = Participation(
            event=self.event2,
            user=self.user,
            standby=False,
            presence_status='P',
        )
        self.participation2.save()

        self.site = AdminSite()
        self.admin = CycleAdmin(Cycle, self.site)

        self.profile = Profile.objects.filter(
            user__pk=self.participation.user.pk,
        ).first()

        self.client = Client()
        self.client.login(username=self.username, password=self.password)

    def test_admin_access(self):
        admin_pages = [
            "/admin/volunteer/",
            "/admin/volunteer/cycle/",
        ]

        for page in admin_pages:
            resp = self.client.get(page)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!DOCTYPE html", str(resp.content))

    def test_admin_participations(self):
        self.assertNotEqual(self.admin, None)

    def test_admin_cycle_participation_export(self):
        change_url = reverse('admin:volunteer_cycle_changelist')

        data = {'action': 'generate_participation_report_csv',
                ACTION_CHECKBOX_NAME: [self.cycle.pk, ]}

        response = self.client.post(change_url, data)

        self.assertEquals(response.status_code, 200)

        self.assertEquals(
            response.content,
            b'first_name,last_name,email,total_time\r\n,,,96\r\n',
        )

    def test_admin_cycle_participation_export_error(self):
        change_url = reverse('admin:volunteer_cycle_changelist')

        data = {'action': 'generate_participation_report_csv',
                ACTION_CHECKBOX_NAME: [self.cycle.pk, self.cycle_inactive.pk]}

        response = self.client.post(change_url, data)

        self.assertEquals(response.status_code, 302)

    def test_admin_cycle_participation_export_error_initialisation(self):
        self.event3 = Event.objects.create(
            cell=self.cell,
            cycle=self.cycle,
            task_type=self.task_type,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        self.participation3 = Participation(
            event=self.event3,
            user=self.user,
            standby=False,
            presence_status='I',
        )
        self.participation3.save()

        change_url = reverse('admin:volunteer_cycle_changelist')

        data = {'action': 'generate_participation_report_csv',
                ACTION_CHECKBOX_NAME: [self.cycle.pk, ]}

        response = self.client.post(change_url, data)

        self.assertEquals(response.status_code, 302)
