import json
from datetime import datetime


from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings

from decouple import config
import responses
from django.conf import settings

from rest_framework.test import APIClient
from django.urls import reverse

import pytz
LOCAL_TIMEZONE = pytz.timezone(settings.TIME_ZONE)



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

from api_volontaria.email import EmailAPI
from api_volontaria.apps.log_management.models import EmailLog


@responses.activate
@override_settings(
    EMAIL_BACKEND='anymail.backends.test.EmailBackend',
    ANYMAIL={
        'SENDINBLUE_API_KEY':
        config('SENDINBLUE_API_KEY', default='placeholder_key'),
        'REQUESTS_TIMEOUT': (30, 30),
        'TEMPLATES': {
            'CONFIRMATION_PARTICIPATION': 57,
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
    },)
class SendCustomEmailTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        # self.user2 = UserFactory()
        # self.user2.set_password('Test123!')
        # self.user2.save()

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

        # self.event2 = Event.objects.create(
        #     start_time=LOCAL_TIMEZONE.localize(datetime(2140, 1, 15, 8)),
        #     end_time=LOCAL_TIMEZONE.localize(datetime(2140, 1, 17, 12)),
        #     nb_volunteers_needed=10,
        #     nb_volunteers_standby_needed=0,
        #     cell=self.cell,
        #     task_type=self.tasktype,
        # )

        self.participation = Participation.objects.create(
            event=self.event,
            user=self.user,
            is_standby=False,
        )

        # self.participation2 = Participation.objects.create(
        #     event=self.event2,
        #     user=self.user2,
        #     is_standby=False,
        # )

    
    def test_send_custom_confirmation_email_2(self):
        
        template = settings.ANYMAIL.get('TEMPLATES')
        template_id = template.get('CONFIRMATION_PARTICIPATION')
        print('test 2')
        print(template_id)
        self.assertEqual(template_id, 57)

        outbox_initial_email_count = len(mail.outbox)
        
        email_log_initial_count = EmailLog.objects.filter(
            user_email=self.user.email,
            type_email='organization custom template email',
            template_id=id
        ).count()
        
        print('custom confirmation')
        print(f'template id: {id}')
        print(f'outbox[0]: {mail.outbox[0].to}')

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

        # 2. proper template?

        email_log_final_count = EmailLog.objects.filter(
            user_email=self.user.email,
            type_email='organization custom template email',
            template_id=id,
        ).count()

        print('custom confirmation log after')
        print(EmailLog.objects.all())

        print(mail.outbox[0].tags)
        self.assertEqual(mail.outbox[0].tags, ["confirmation"])

        self.assertEqual(
            email_log_final_count,
            email_log_initial_count + 1,
        )


# # Assume our app has a signup view that accepts an email address...
#     def test_sends_confirmation_email(self):
#         self.client.post("/account/signup/", {"email": "user@example.com"})
#         print('Signup test case a ete teste')
#         # Test that one message was sent:
#         self.assertEqual(len(mail.outbox), 1)

#         # Verify attributes of the EmailMessage that was sent:
#         self.assertEqual(mail.outbox[0].to, ["user@example.com"])
#         self.assertEqual(mail.outbox[0].tags, ["confirmation"])  # an Anymail custom attr

#         # Or verify the Anymail params, including any merged settings defaults:
#         self.assertTrue(mail.outbox[0].anymail_test_params["track_clicks"])
