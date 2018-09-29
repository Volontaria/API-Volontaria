from django.conf import settings
from django.core.mail import send_mail

def service_send_mail(emails, subject, plain_msg, msg_html):
    """
    Uses Anymail to send templated emails.
    Returns a list of email addresses to which emails failed to be delivered.
    """
    results = []
    for email in emails:
        nb_sent_emails = send_mail(
            subject,
            plain_msg,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=msg_html,
        )
        # nb_sent_emails = 1 if mail sent
        # nb_sent_emails = 0 if mail failed
        if(bool(nb_sent_emails) == False):
            results.append(email)

    return results