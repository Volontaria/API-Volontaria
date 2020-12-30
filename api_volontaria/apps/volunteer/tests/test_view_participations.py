import json
from datetime import datetime
from decouple import config

from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse

from django.core import mail
from django.test.utils import override_settings

import responses

from api_volontaria.email import EmailAPI
from api_volontaria.apps.log_management.models import EmailLog

from api_volontaria.apps.volunteer.models import (
    Participation,
    Cell,
    TaskType,
    Event,
)
from api_volontaria.factories import (
    UserFactory,
    AdminFactory,
)
from api_volontaria.testClasses import CustomAPITestCase

import pytz
from django.conf import settings
LOCAL_TIMEZONE = pytz.timezone(settings.TIME_ZONE)


class ParticipationsTests(CustomAPITestCase):

    ATTRIBUTES = [
        'id',
        'url',
        'event',
        'user',
        'presence_duration_minutes',
        'presence_status',
        'is_standby',
        'registered_at',
    ]

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

        self.cell = Cell.objects.create(
            name='My new cell',
            address_line_1='373 Rue villeneuve E',
            postal_code='H2T 1M1',
            city='Montreal',
            state_province='Quebec',
            longitude='45.540237',
            latitude='-73.603421',
        )

        self.tasktype = TaskType.objects.create(
            name='My new tasktype',
        )

        self.event = Event.objects.create(
            start_time=LOCAL_TIMEZONE.localize(datetime(2140, 1, 15, 8)),
            end_time=LOCAL_TIMEZONE.localize(datetime(2140, 1, 17, 12)),
            nb_volunteers_needed=10,
            nb_volunteers_standby_needed=0,
            cell=self.cell,
            task_type=self.tasktype,
        )

        self.event2 = Event.objects.create(
            start_time=LOCAL_TIMEZONE.localize(datetime(2140, 1, 15, 8)),
            end_time=LOCAL_TIMEZONE.localize(datetime(2140, 1, 17, 12)),
            nb_volunteers_needed=10,
            nb_volunteers_standby_needed=0,
            cell=self.cell,
            task_type=self.tasktype,
        )

        self.participation = Participation.objects.create(
            event=self.event2,
            user=self.user,
            is_standby=False,
        )

        self.participation2 = Participation.objects.create(
            event=self.event2,
            user=self.user2,
            is_standby=False,
        )

    def test_create_new_participation_as_admin(self):
        """
        Ensure we can create a new participation if we are an admin.
        """
        data_post = {
            'event': reverse(
                'event-detail',
                args=[self.event.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.admin.id],
            ),
            'is_standby': False,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('participation-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            content
        )
        self.check_attributes(content)

    def test_create_new_participation(self):
        """
        Ensure we can create a new participation if we are a simple user.
        """
        data_post = {
            'event': reverse(
                'event-detail',
                args=[self.event.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user.id],
            ),
            'is_standby': False,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('participation-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            content
        )
        self.check_attributes(content)

    def test_create_new_participation_for_an_other_user(self):
        """
        Ensure we can't create a new participation for an other user
        if we are a simple user.
        """
        data_post = {
            'event': reverse(
                'event-detail',
                args=[self.event.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user2.id],
            ),
            'is_standby': False,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('participation-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            content
        )
        self.assertEqual(
            content,
            {
                'user': [
                    "You don't have the right to create a participation "
                    "for an other user"
                ]
            }
        )

    def test_create_new_participation_for_an_other_user_as_admin(self):
        """
        Ensure we can create a new participation for an other user
        if we are an administrator.
        """
        data_post = {
            'event': reverse(
                'event-detail',
                args=[self.event.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user2.id],
            ),
            'is_standby': False,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('participation-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            content
        )
        self.check_attributes(content)

    def test_update_participation_as_admin(self):
        """
        Ensure we can update a participation if we are an admin.
        """
        new_value = True
        data_post = {
            'is_standby': new_value,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'participation-detail',
                kwargs={
                    'pk': self.participation.id
                },
            ),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_attributes(content)
        self.assertEqual(content['is_standby'], new_value)

    def test_update_participation(self):
        """
        Ensure we can't update a participation if we are a simple user.
        """
        new_value = True
        data_post = {
            'is_standby': new_value,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'participation-detail',
                kwargs={
                    'pk': self.participation.id
                },
            ),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            content,
            {
                'detail': 'You do not have permission to perform this action.'
            }
        )

    def test_delete_participation_as_admin(self):
        """
        Ensure we can delete a participation if we are an admin.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'participation-detail',
                kwargs={
                    'pk': self.participation.id
                },
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')

    def test_delete_participation(self):
        """
        Ensure we can't delete a participation if we are a simple user.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'participation-detail',
                kwargs={
                    'pk': self.participation.id
                },
            )
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            content,
            {
                'detail': 'You do not have permission to perform this action.'
            }
        )

    def test_list_participations(self):
        """
        Ensure we can list participations.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse('participation-list'),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content['results']), 1)
        self.check_attributes(content['results'][0])

        for participation in content['results']:
            self.assertEqual(
               participation['user']['id'],
               self.user.id,
            )

    def test_list_participations_as_admin(self):
        """
        Ensure we can list all the participations where we are administrator
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse('participation-list'),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content['results']), 2)
        self.check_attributes(content['results'][0])

        at_least_one_participation_is_owned_by_somebody_else = False
        for participation in content['results']:
            if participation['user']['id'] != self.admin.id:
                at_least_one_participation_is_owned_by_somebody_else = True

        self.assertTrue(at_least_one_participation_is_owned_by_somebody_else)

    @override_settings(
        EMAIL_BACKEND='anymail.backends.test.EmailBackend',
        ANYMAIL={
            'SENDINBLUE_API_KEY':
            config('SENDINBLUE_API_KEY', default='placeholder_key'),
            'REQUESTS_TIMEOUT': (30, 30),
            'TEMPLATES': {
                'CONFIRMATION_PARTICIPATION': 3,
                # set template id to 3 when no template has been defined
                # in settings.py (or .env)
                # if template id already set in settings,
                # then 3 does not override
                # that template id (see comment further below about
                # test logic as a result)
                'CANCELLATION_PARTICIPATION_EMERGENCY': config(
                    'TEMPLATE_ID_CANCELLATION_PARTICIPATION_EMERGENCY',
                    default=0,
                    cast=int
                ),
                'RESET_PASSWORD': config(
                    'RESET_PASSWORD_EMAIL_TEMPLATE',
                    default=0
                ),
            }
        }
    )
    def test_send_custom_confirmation_email(self):
        """ Ensure that
        1. an email is sent to participant
        when a participation gets created
        2.a. email uses custom template vs. Volontaria default
        (case when a template has been set up by organization
        on their Sendinblue account)
        2.b. the right template is sent
        (participation confirmation vs. cancellation)
        """
        outbox_initial_email_count = len(mail.outbox)

        email_log_initial_count = EmailLog.objects.filter(
            user_email=[self.user.email],
            type_email='CONFIRMATION_PARTICIPATION',
            template_id__isnull=False,
            # template_id in settings cannot be overriden
            # (some cache applied to ANYMAIL settings?)
            # see https://stackoverflow.com/questions/53953444/
            # overriding-settings-in-django-when-used-by-the-models#59043355
            # so we do not test for a specific template id #)
        ).count()

        data_post = {
            'event': reverse(
                'event-detail',
                args=[self.event.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user.id],
            ),
            'is_standby': False,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('participation-list'),
            data_post,

            format='json',
        )

        # 1. email sent?
        nb_email_sent = len(mail.outbox) - outbox_initial_email_count

        # 2.a and 2.b: proper template?

        email_log_final_count = EmailLog.objects.filter(
            user_email=[self.user.email],
            type_email='CONFIRMATION_PARTICIPATION',
            template_id__isnull=False,
        ).count()

        self.assertEqual(
            email_log_final_count,
            email_log_initial_count + 1,
        )

    @override_settings(
        EMAIL_BACKEND='anymail.backends.test.EmailBackend',
        ANYMAIL={
            'SENDINBLUE_API_KEY':
            config('SENDINBLUE_API_KEY', default='placeholder_key'),
            'REQUESTS_TIMEOUT': (30, 30),
            'TEMPLATES': {
                'CONFIRMATION_PARTICIPATION': 0,
                'CANCELLATION_PARTICIPATION_EMERGENCY': config(
                    'TEMPLATE_ID_CANCELLATION_PARTICIPATION_EMERGENCY',
                    default=0,
                    cast=int
                ),
                'RESET_PASSWORD': config(
                    'RESET_PASSWORD_EMAIL_TEMPLATE',
                    default=0
                ),
            }
        }
    )
    def test_send_default_confirmation_email(self):
        """
        Ensure that
        1. an email is sent to participant
        when a participation gets created
        2.a. email uses Volontaria default template
        (case when no template has been set up by organization
        on their Sendinblue account)
        2.b. the right template is sent
        (participation confirmation vs. cancellation)
        """

        outbox_initial_email_count = len(mail.outbox)

        email_log_initial_count = EmailLog.objects.filter(
            user_email=[self.user.email],
            type_email='Objet: Confirmation de participation',
            template_id__isnull=True,
        ).count()

        data_post = {
            'event': reverse(
                'event-detail',
                args=[self.event.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user.id],
            ),
            'is_standby': False,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('participation-list'),
            data_post,

            format='json',
        )

        # 1. email sent?
        nb_email_sent = len(mail.outbox) - outbox_initial_email_count

        # 2.a and 2.b: proper template?

        email_log_final_count = EmailLog.objects.filter(
            user_email=[self.user.email],
            type_email='Objet: Confirmation de participation',
            template_id__isnull=True,
        ).count()

        self.assertEqual(
            email_log_final_count,
            email_log_initial_count + 1,
        )

    @override_settings(
        EMAIL_BACKEND='anymail.backends.test.EmailBackend',
        NUMBER_OF_DAYS_BEFORE_EMERGENCY_CANCELLATION=99999,
        ANYMAIL={
            'SENDINBLUE_API_KEY':
            config('SENDINBLUE_API_KEY', default='placeholder_key'),
            'REQUESTS_TIMEOUT': (30, 30),
            'TEMPLATES': {
                'CONFIRMATION_PARTICIPATION': 3,
                'CANCELLATION_PARTICIPATION_EMERGENCY': 4,
                # same logic
                # as in test_send_custom_confirmation_email)
                'RESET_PASSWORD': config(
                    'RESET_PASSWORD_EMAIL_TEMPLATE',
                    default=0
                ),
            }
        }
    )
    def test_send_custom_cancellation_email(self):
        """
        Ensure that
        1. an email is sent to organization
        when a participation gets cancelled
        2.a. email uses custom template
        (case when a template has been set up by organization
        on their Sendinblue account)
        2.b. the right template is sent
        (cancellation)
        """

        outbox_initial_email_count = len(mail.outbox)

        email_log_initial_count = EmailLog.objects.filter(
            user_email=[settings.LOCAL_SETTINGS['CONTACT_EMAIL']],
            type_email='CANCELLATION_PARTICIPATION_EMERGENCY',
            template_id__isnull=False,
        ).count()

        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'participation-detail',
                kwargs={
                    'pk': self.participation.id
                },
            )
        )

        # 1. email sent?
        nb_email_sent = len(mail.outbox) - outbox_initial_email_count

        self.assertEqual(nb_email_sent, 1)

        # 2.a. and 2.b. proper template?

        email_log_final_count = EmailLog.objects.filter(
            user_email=[settings.LOCAL_SETTINGS['CONTACT_EMAIL']],
            type_email='CANCELLATION_PARTICIPATION_EMERGENCY',
            template_id__isnull=False,
        ).count()

        self.assertEqual(
            email_log_final_count,
            email_log_initial_count + 1,
        )

    @override_settings(
        EMAIL_BACKEND='anymail.backends.test.EmailBackend',
        NUMBER_OF_DAYS_BEFORE_EMERGENCY_CANCELLATION=99999,
        ANYMAIL={
            'SENDINBLUE_API_KEY':
            config('SENDINBLUE_API_KEY', default='placeholder_key'),
            'REQUESTS_TIMEOUT': (30, 30),
            'TEMPLATES': {
                'CONFIRMATION_PARTICIPATION': config(
                    'TEMPLATE_ID_CONFIRMATION_PARTICIPATION',
                    default=0,
                    cast=int
                ),
                'CANCELLATION_PARTICIPATION_EMERGENCY': 0,
                # Template numbering starts at 1
                # in SendinBlue Email templates lists,
                # so id=0 here implies no template has been defined
                # by non-profit organization
                'RESET_PASSWORD': config(
                    'RESET_PASSWORD_EMAIL_TEMPLATE',
                    default=0
                ),
            }
        }
    )
    def test_send_default_cancellation_email(self):
        """
        Ensure that
        1. an email is sent to organization
        when a participation gets cancelled
        2.a. email uses Volontaria default template
        (case when no template has been set up by organization
        on their Sendinblue account)
        2.b. the right template is sent
        (cancellation)
        """

        outbox_initial_email_count = len(mail.outbox)

        email_log_initial_count = EmailLog.objects.filter(
            user_email=[settings.LOCAL_SETTINGS['CONTACT_EMAIL']],
            type_email='Objet: Annulation de participation',
            template_id__isnull=True,
        ).count()

        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'participation-detail',
                kwargs={
                    'pk': self.participation.id
                },
            )
        )
        # 1. email sent?
        nb_email_sent = len(mail.outbox) - outbox_initial_email_count

        self.assertEqual(nb_email_sent, 1)

        # 2. proper template?
        email_log_final_count = EmailLog.objects.filter(
            user_email=[settings.LOCAL_SETTINGS['CONTACT_EMAIL']],
            type_email='Objet: Annulation de participation',
            template_id__isnull=True,
        ).count()

        self.assertEqual(
            email_log_final_count,
            email_log_initial_count + 1,
        )
