from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from api_volontaria import settings, front_end_url

TEMPLATES = settings.ANYMAIL.get('TEMPLATES')


class EmailAPI:

    def send_email(
            self,
            subject, message, from_email, recipient_list,
            fail_silently=False, auth_user=None, auth_password=None,
            connection=None, html_message=None):
        return django_send_mail(
                subject, message, from_email, recipient_list,
                fail_silently, auth_user, auth_password,
                connection, html_message
            )

    def get_generic_information(self):
        contact_email = settings.LOCAL_SETTINGS['CONTACT_EMAIL']

        return {
            "MAIL_NAME_CONTACT": contact_email,
        }

    def send_template_email(self, email, template, context):

        email_context = self.get_generic_information()
        email_context.update(context)

        message = EmailMessage(
            subject=None,  # required for SendinBlue templates
            body='',  # required for SendinBlue templates
            to=[email]
        )
        message.from_email = None  # required for SendinBlue templates
        # use this SendinBlue template
        message.template_id = TEMPLATES.get(template)
        message.merge_global_data = email_context

        # return number of successfully sent emails
        return message.send()

    def get_messages(self, template_name, merge_data):
        plain_msg = render_to_string(
            f'{template_name}.txt',
            merge_data
        )
        msg_html = render_to_string(
            f'{template_name}.html',
            merge_data
        )

        return plain_msg, msg_html
