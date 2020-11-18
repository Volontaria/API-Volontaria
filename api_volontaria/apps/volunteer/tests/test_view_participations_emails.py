from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings

from decouple import config
import responses
from django.conf import settings

# @responses.activate
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
class SignupTestCase(TestCase):
    
    def test_send_custom_confirmation_email_2(self):
        template = settings.ANYMAIL.get('TEMPLATES')
        template_id = template.get('CONFIRMATION_PARTICIPATION')
        print('test 2')
        print(template_id)
        self.assertEqual(template_id, 57)



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
