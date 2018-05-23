import csv
import json
import shutil
import tempfile

from unittest import mock

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.test.utils import override_settings

from apiVolontaria.factories import UserFactory, AdminFactory
from location.models import Address, StateProvince, Country
from ..models import Cell, Event, Cycle, TaskType, Participation


class CellExportationTests(APITestCase):

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

            self.participation3 = Participation.objects.create(
                standby=True,
                user=self.user2,
                event=self.event,
            )

            "Create temp directory and update MEDIA_ROOT and default storage."
            settings._original_media_root = settings.MEDIA_ROOT
            settings._original_file_storage = settings.DEFAULT_FILE_STORAGE
            self._temp_media = tempfile.mkdtemp()
            settings.MEDIA_ROOT = self._temp_media
            settings.DEFAULT_FILE_STORAGE = \
                'django.core.files.storage.FileSystemStorage'

    def tearDown(self):
        "Delete temp storage."
        shutil.rmtree(self._temp_media, ignore_errors=True)
        settings.MEDIA_ROOT = settings._original_media_root
        del settings._original_media_root
        settings.DEFAULT_FILE_STORAGE = settings._original_file_storage
        del settings._original_file_storage

    @override_settings(DEBUG=True)
    def test_cell_exportation(self):
        """
        Ensure we can export Participation from a Cell.
        """

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            '/volunteer/cells/%s/export' % self.cell.pk,
            format='json',
        )

        content = json.loads(response.content)

        # get today date without time
        now = timezone.now()
        now = now.replace(hour=0, minute=0, second=0, microsecond=0)

        actual_file_path = \
            '/%scell_export/%s_%s.csv' % \
            (settings.MEDIA_URL, self.cell.pk, now.strftime('%Y%m%d'))

        data_compare = {
            'export_link': actual_file_path
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content, data_compare)

        data = [
            'standby,first_name,last_name,email,phone,mobile,'
            'event__start_date,event__end_date,task_type,'
            'cell,presence_status,presence_duration_minutes\n',

            '1,%s,%s,%s,,,%s,%s,%s,%s,%s,\n' % (
                self.participation2.user.first_name,
                self.participation2.user.last_name,
                self.participation2.user.email,
                self.participation2.event.start_date
                    .strftime("%Y-%m-%d %H:%M:%S"),
                self.participation2.event.end_date
                    .strftime("%Y-%m-%d %H:%M:%S"),
                self.participation2.event.task_type.name,
                self.participation2.cell,
                self.participation2.presence_status,
            ),

            '1,%s,%s,%s,,,%s,%s,%s,%s,%s,\n' % (
                self.participation.user.first_name,
                self.participation.user.last_name,
                self.participation.user.email,
                self.participation.event.start_date
                    .strftime("%Y-%m-%d %H:%M:%S"),
                self.participation.event.end_date
                    .strftime("%Y-%m-%d %H:%M:%S"),
                self.participation.event.task_type.name,
                self.participation.cell,
                self.participation.presence_status,
            ),

            '1,%s,%s,%s,,,%s,%s,%s,%s,%s,\n' % (
                self.participation3.user.first_name,
                self.participation3.user.last_name,
                self.participation3.user.email,
                self.participation3.event.start_date
                    .strftime("%Y-%m-%d %H:%M:%S"),
                self.participation3.event.end_date
                    .strftime("%Y-%m-%d %H:%M:%S"),
                self.participation3.event.task_type.name,
                self.participation3.cell,
                self.participation3.presence_status,
            )]

        actual_file_path = \
            '%s/cell_export/%s_%s.csv' % \
            (self._temp_media, self.cell.pk, now.strftime('%Y%m%d'))

        with open(actual_file_path) as fp:
            line = fp.readline()
            cnt = 0
            while line:

                self.assertEqual(line, data[cnt])

                line = fp.readline()
                cnt += 1
