import json
from unittest.mock import patch

from django.test import override_settings
from django.utils import timezone
from unittest import mock

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apiVolontaria.factories import UserFactory, AdminFactory
from location.models import Address, StateProvince, Country
from ..models import Cell, TaskType, Cycle, Event, Participation

USER_EMAIL = 'test1@example.com'


class CellsEmailTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.email = USER_EMAIL
        self.user.set_password('Test123!')

        self.user.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

        self.random_country = Country.objects.create(
            name="Random Country",
            iso_code="RC",
        )
        self.random_state_province = StateProvince.objects.create(
            name="Random State",
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
            name='my cell',
            address=self.address,
        )

        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(
            minutes=100,
        )

        self.cycle = Cycle.objects.create(
            name='my cycle',
            start_date=start_date,
            end_date=end_date,
        )

        self.task_type = TaskType.objects.create(
            name='my tasktype'
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

    def test_create_email_no_subject(self):
        """
        Ensure we cannot send an email without the subject field.
        """

        self.client.force_authenticate(user=self.admin)

        data_post = {
            'content': 'test',
        }

        response = self.client.post(
            '/volunteer/cells/%s/email' % self.cell.pk,
            data_post,
            format='json',
        )

        content = json.loads(response.content)
        self.assertEqual(content, {'subject': ['This field is required.']})

    def test_create_email_no_content(self):
        """
        Ensure we cannot send an email without the content field.
        """

        self.client.force_authenticate(user=self.admin)

        data_post = {
            'subject': 'test',
        }

        response = self.client.post(
            '/volunteer/cells/%s/email' % self.cell.pk,
            data_post,
            format='json',
        )

        content = json.loads(response.content)
        self.assertEqual(content, {'content': ['This field is required.']})

    def test_create_email(self):
        """
        Ensure we cannot send an email.
        """

        self.client.force_authenticate(user=self.admin)

        data_post = {
            'subject': 'test',
            'content': 'test',
        }

        response = self.client.post(
            '/volunteer/cells/%s/email' % self.cell.pk,
            data_post,
            format='json',
        )

        content = json.loads(response.content)
        self.assertEqual(content, {'emails': [self.user.email]})

    @override_settings(CUSTOM_EMAIL=True)
    def test_create_email_filters(self):
        """
        Ensure we cannot send an email with filters for the Cycle and the Tasktype.
        """

        self.client.force_authenticate(user=self.admin)

        data_post = {
            'subject': 'test',
            'content': 'test',
        }

        response = self.client.post(
            '/volunteer/cells/%s/email?cycle=%s&task=%s' % (self.cell.pk, self.cycle.pk, self.task_type.pk),
            data_post,
            format='json',
        )

        content = json.loads(response.content)
        self.assertEqual(content, {'emails': [self.user.email]})

    @override_settings(CUSTOM_EMAIL=True)
    @patch('apiVolontaria.services.service_send_mail', return_value=[USER_EMAIL])
    def test_create_email_failed_send_email(self, service_send_mail):
        """
        Test the case when the email sending is failing.
        We mock the return value of apiVolontaria.services.service_send_mail to get the 400 response
        """

        self.client.force_authenticate(user=self.admin)

        data_post = {
            'subject': 'test',
            'content': 'test',
        }

        response = self.client.post(
            '/volunteer/cells/%s/email' % self.cell.pk,
            data_post,
            format='json',
        )

        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content, {'detail': 'No email sended. Please contact the administration.'})
