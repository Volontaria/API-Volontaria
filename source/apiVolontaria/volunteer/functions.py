from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from ics import Calendar, Event

def generate_participation_ics(participation, path_event_file):
    calendar = Calendar()
    event = Event()

    event.name = settings.CONSTANT["CALENDAR_EVENT_NAME"] + \
                 participation.event.cycle.name
    event.begin = participation.event.start_date
    event.end = participation.event.end_date
    calendar.events.add(event)

    # create a ics file
    try:
        with open(path_event_file, 'w') as my_file:
            my_file.writelines(calendar)
    except:
        raise serializers.ValidationError({
            'content': [
                _(
                    "ics fille was not created, try again to create a participation. "
                    "If it still does not work, please contact the support."
                )
            ],
        })
