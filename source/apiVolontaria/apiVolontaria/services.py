import json
from datetime import datetime

import pytz
import re

from django.apps import apps
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from rest_framework.pagination import PageNumberPagination

from log_management.models import Log, EmailLog
from .exceptions import MailServiceError
from django.core.mail import send_mail as django_send_mail

from rest_framework.utils.urls import remove_query_param, replace_query_param

LOCAL_TIMEZONE = pytz.timezone(settings.TIME_ZONE)


def send_templated_email(users, context, template):
    """
    Uses Anymail to send templated emails.
    Returns a list of email addresses to which emails failed to be delivered.
    """
    if settings.CONSTANT['EMAIL_SERVICE'] is False:
        raise MailServiceError(_(
            "Email service is disabled."
        ))
    MAIL_SERVICE = settings.ANYMAIL

    failed_emails = list()
    for user in users:
        message = EmailMessage(
            subject=None,  # required for SendinBlue templates
            body='',  # required for SendinBlue templates
            to=[user.email]
        )
        message.from_email = None  # required for SendinBlue templates
        # use this SendinBlue template
        message.template_id = MAIL_SERVICE["TEMPLATES"].get(template)
        message.merge_global_data = context
        try:
            # return number of successfully sent emails
            response = message.send()
            EmailLog.add(user.email, template, response)
        except Exception as err:
            additional_data = {
                'email': user.email,
                'context': context,
                'template': template
            }
            Log.error(
                source='SENDING_BLUE_TEMPLATE',
                message=err,
                additional_data=json.dumps(additional_data)
            )
            raise

        if not response:
            failed_emails.append(user.email)

    return failed_emails


def send_sign_up_validation_email(user, url_of_activation):
    """
    This function sends an email to a new signed up user in order to allow
    him to validate his email address and activate his account.
    :param user: The user that want to validate his email address
    :param url_of_activation: The url where the user need to go to validate
    his account
    :return: None
    """

    context = {
        'USER_FIRST_NAME': user.first_name,
        'USER_LAST_NAME': user.last_name,
        'USER_EMAIL': user.email,
        'VALIDATION_URL': url_of_activation,
    }

    send_templated_email(
        [user],
        context,
        'CONFIRM_SIGN_UP'
    )
