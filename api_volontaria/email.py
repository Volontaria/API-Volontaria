from django.core.mail import send_mail as django_send_mail
from django.core.mail import EmailMessage

from api_volontaria import settings

from api_volontaria.apps.log_management.models import EmailLog

TEMPLATES = settings.ANYMAIL.get('TEMPLATES')


class EmailAPI:

    def send_email(
            self,
            subject, message, from_email, recipient_list,
            fail_silently=False, auth_user=None, auth_password=None,
            connection=None, html_message=None):
        ''' sending and logging emails '''

        nb_email_successfully_sent = django_send_mail(
                subject, message, from_email, recipient_list,
                fail_silently, auth_user, auth_password,
                connection, html_message
            )

        EmailLog.add(
            user_email=recipient_list,
            nb_email_sent=nb_email_successfully_sent,
            type_email=subject,
        )

        return nb_email_successfully_sent

    def get_generic_information(self):
        contact_email = settings.LOCAL_SETTINGS['CONTACT_EMAIL']

        return {
            "MAIL_NAME_CONTACT": contact_email,
            "VOLONTARIA_WEBSITE_URL": 'https://volontaria.github.io/'
        }

    def send_template_email(self, email, template, context):
        ''' sending email using SendinBlue templates,
        and logging email
        '''

        email_context = context
        email_context['GENERIC'] = self.get_generic_information()

        message = EmailMessage(
            subject=None,  # required for SendinBlue templates
            body='',  # required for SendinBlue templates
            to=[email],
        )
        message.from_email = None  # required for SendinBlue templates

        # use this SendinBlue template
        message.template_id = TEMPLATES.get(template)

        message.merge_global_data = email_context

        nb_email_successfully_sent = message.send()

        EmailLog.add(
            user_email=[email],
            type_email=template,
            nb_email_sent=nb_email_successfully_sent,
            template_id=TEMPLATES.get(template),
        )

        return nb_email_successfully_sent
