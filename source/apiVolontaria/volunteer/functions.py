from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from icalendar import Calendar, Event as ICalEvent
from babel.dates import format_datetime


def generate_ics(event):
    """
    This will construct a calendar from an Event object
    """
    cal = Calendar()

    cal.add('prodid', '-//{0}//'.format(event.task_type.name, ))
    cal.add('version', '2.0')

    ical_event = ICalEvent()
    ical_event.add('summary', u'NousRire - %s' % event.task_type.name)
    ical_event.add('dtstart', event.start_date)
    ical_event.add('dtend', event.end_date)
    ical_event.add('dtstamp', event.end_date)
    ical_event.add('location', event.cell.address)
    ical_event['uid'] = str(event.id)

    cal.add_component(ical_event)

    return cal.to_ical()


def generate_email_invitation(participation):
    """
    This will generate an email to a user sending a calendar invitation
    """

    calendar = generate_ics(participation.event)

    if settings.CONSTANT['EMAIL_SERVICE'] is True:

        email_to = participation.user.email

        # Debug Mode checking if we have an email in DEBUG_EMAIL_TO
        # or disable the sending of email
        if settings.DEBUG:
            email_to = settings.DEBUG_EMAIL_TO

        msg = EmailMultiAlternatives(
            subject=None,
            body=None,
            to=[email_to, ],
        )

        msg.attach('invitations.ics', calendar.decode(), 'text/calendar')

        msg.from_email = None
        msg.template_id = settings.SENDINBLUE_TEMPLATE['CALENDAR_INVITATION']

        date = u'%s%s' % (
            format_datetime(participation.event.start_date.astimezone(), "EEEE 'le' dd MMMM 'de' HH:mm 'à' ", locale='fr'),
            participation.event.end_date.astimezone().strftime("%H:%M"),
        )

        msg.merge_global_data = {
            'activity': participation.event.task_type.name,
            'location': participation.event.cell.address.__str__(),
            'date': date,
        }

        # Send only if we have a value in email_to
        if email_to:
            msg.send()
