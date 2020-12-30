from datetime import datetime, timedelta
import pytz
from babel.dates import format_date
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from dry_rest_permissions.generics import authenticated_users
from api_volontaria.email import EmailAPI


User = get_user_model()


class Cell(models.Model):
    """
    This class represents a physical place where volunteer can go to help.
    """

    class Meta:
        verbose_name = _("Cell")
        verbose_name_plural = _('Cells')

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=100,
    )

    address_line_1 = models.CharField(
        max_length=100,
        verbose_name=_("Address line 1"),
    )

    address_line_2 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Address line 2"),
    )

    postal_code = models.CharField(
        max_length=10,
        verbose_name=_("Postal code"),
    )

    state_province = models.CharField(
        max_length=100,
        verbose_name=_("State/Province"),
    )

    city = models.CharField(
        max_length=50,
        blank=False,
        verbose_name=_("City"),
    )

    latitude = models.FloatField(
        verbose_name=_("Latitude"),
    )

    longitude = models.FloatField(
        verbose_name=_("Longitude"),
    )

    def __str__(self):
        return self.name

    @staticmethod
    def has_create_permission(request):
        if request.user.is_staff:
            return True
        else:
            return False

    @authenticated_users
    def has_object_destroy_permission(self, request):
        if request.user.is_staff:
            return True
        else:
            return False

    @authenticated_users
    def has_object_update_permission(self, request):
        if request.user.is_staff:
            return True
        else:
            return False


class TaskType(models.Model):
    """
    This class represents a type of task that the volunteer can do during
    an event.
    """

    class Meta:
        verbose_name = _('TaskType')
        verbose_name_plural = _('TaskTypes')

    name = models.CharField(
        verbose_name="Name",
        max_length=100,
    )

    def __str__(self):
        return self.name

    @staticmethod
    def has_create_permission(request):
        if request.user.is_staff:
            return True
        else:
            return False

    @authenticated_users
    def has_object_destroy_permission(self, request):
        if request.user.is_staff:
            return True
        else:
            return False

    @authenticated_users
    def has_object_update_permission(self, request):
        if request.user.is_staff:
            return True
        else:
            return False


class Event(models.Model):
    """
    This class represents an event where volunteer can come to help.
    """

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _('Events')

    description = models.TextField(
        verbose_name="Description",
    )

    start_time = models.DateTimeField(
        verbose_name=_("Begin date"),
    )

    end_time = models.DateTimeField(
        verbose_name=_("End date"),
    )

    nb_volunteers_needed = models.PositiveIntegerField(
        verbose_name=_("Number of volunteers (needed)"),
        default=0,
    )

    nb_volunteers_standby_needed = models.PositiveIntegerField(
        verbose_name=_("Number of volunteers on hold (needed)"),
        default=0,
    )

    volunteers = models.ManyToManyField(
        User,
        verbose_name=_("Volunteers"),
        related_name="events",
        blank=True,
        through='Participation',
    )

    cell = models.ForeignKey(
        Cell,
        verbose_name=_("Cell"),
        blank=False,
        on_delete=models.CASCADE,
    )

    task_type = models.ForeignKey(
        TaskType,
        verbose_name="Task type",
        blank=False,
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return str(self.start_time) + ' - ' + str(self.end_time)

    @property
    def is_started(self):
        return self.start_time <= timezone.now()

    @property
    def is_finished(self):
        return self.end_time <= timezone.now()

    @property
    def nb_volunteers(self):
        return Participation.objects.filter(
            is_standby=False,
            event=self,
        ).count()

    @property
    def nb_volunteers_standby(self):
        return Participation.objects.filter(
            is_standby=True,
            event=self,
        ).count()

    @property
    def duration(self):
        return self.end_time - self.start_time

    @staticmethod
    def has_create_permission(request):
        if request.user.is_staff:
            return True
        else:
            return False

    @authenticated_users
    def has_object_destroy_permission(self, request):
        if request.user.is_staff:
            return True
        else:
            return False

    @authenticated_users
    def has_object_update_permission(self, request):
        if request.user.is_staff:
            return True
        else:
            return False


class Participation(models.Model):
    """
    This class represents a participation of a volunteer to a specific event.
    """

    PRESENCE_UNKNOWN = 'UNKNOWN'
    PRESENCE_ABSENT = 'ABSENT'
    PRESENCE_PRESENT = 'PRESENT'

    PRESENCE_CHOICES = (
        (PRESENCE_UNKNOWN, _('Unknown')),
        (PRESENCE_ABSENT, _('Absent')),
        (PRESENCE_PRESENT, _('Present')),
    )

    class Meta:
        verbose_name = _('Participation')
        verbose_name_plural = _('Participations')
        unique_together = ('event', 'user')

    event = models.ForeignKey(
        Event,
        related_name='participations',
        on_delete=models.CASCADE,
    )

    user = models.ForeignKey(
        User,
        related_name='participations',
        on_delete=models.CASCADE,
    )

    presence_duration_minutes = models.PositiveIntegerField(
        verbose_name=_("Presence duration (in minutes)"),
        default=None,
        blank=True,
        null=True,
    )

    presence_status = models.CharField(
        verbose_name=_("Presence status"),
        max_length=100,
        choices=PRESENCE_CHOICES,
        default=PRESENCE_UNKNOWN
    )

    is_standby = models.BooleanField(
        verbose_name=_("Is Stand-By"),
    )

    registered_at = models.DateTimeField(
        verbose_name=_("Registered at"),
        auto_now_add=True,
    )

    def send_email_confirmation(self):
        start_time = self.event.start_time
        start_time = start_time.astimezone(pytz.timezone('US/Eastern'))

        end_time = self.event.end_time
        end_time = end_time.astimezone(pytz.timezone('US/Eastern'))

        type_participation = 'Bénévole'
        if self.is_standby:
            type_participation = 'Remplaçant'

        context = {
            'PARTICIPATION': {
                'FIRST_NAME': self.user.first_name,
                'LAST_NAME': self.user.last_name,
                'TYPE': type_participation
            },
            'ACTIVITY': {
                'NAME': self.event.task_type.name,
                'START_DATE': format_date(
                    start_time,
                    format='long',
                    locale='fr'
                ),
                'START_TIME': start_time.strftime('%-Hh%M'),
                'END_TIME': end_time.strftime('%-Hh%M'),
            },
            'CELL': {
                'NAME': self.event.cell.name,
                'ADDRESS_LINE_1': self.event.cell.address_line_1,
                'ADDRESS_LINE_2': self.event.cell.address_line_2,
                'POSTAL_CODE': self.event.cell.postal_code,
                'CITY': self.event.cell.city,
                'STATE_PROVINCE': self.event.cell.state_province,
            },
            'ORGANIZATION_NAME': settings.LOCAL_SETTINGS['ORGANIZATION'],
        }

        TEMPLATES = settings.ANYMAIL.get('TEMPLATES')
        id = TEMPLATES.get('CONFIRMATION_PARTICIPATION')
        if id:
            EmailAPI().send_template_email(
                self.user.email,
                'CONFIRMATION_PARTICIPATION',
                context,
            )
        else:
            msg_file_name = 'participation_confirmation_email'
            plain_msg = render_to_string(
                '.'.join([msg_file_name, 'txt']),
                context
            )
            msg_html = render_to_string(
                '.'.join([msg_file_name, 'html']),
                context
            )

            EmailAPI().send_email(
                "Objet: Confirmation de participation",
                plain_msg,
                "email_from@mondomain.ca",
                [self.user.email],
                html_message=msg_html,
            )

    def send_email_cancellation_emergency(self):
        """
        An email to inform the administrator that a user just cancel his
        reservation despite the fact that the event is really soon
        :return: message file name (helps determine which type of email
        template has been used, for example when testing application)
        """
        start_time = self.event.start_time
        start_time = start_time.astimezone(pytz.timezone('US/Eastern'))

        end_time = self.event.end_time
        end_time = end_time.astimezone(pytz.timezone('US/Eastern'))

        # Headcount is "pre-delete";
        # but email needs to show headcount after deletion.
        # (and this only applies to actual participations
        # (i.e. non-standby) since, when standby participation gets
        # cancelled, no email gets sent)
        if not self.is_standby:
            updated_volunteer_count = self.event.nb_volunteers - 1

        context = {
            'PARTICIPANT': {
                'FIRST_NAME': self.user.first_name,
                'LAST_NAME': self.user.last_name,
            },
            'ACTIVITY': {
                'NAME': self.event.task_type.name,
                'START_DATE': format_date(
                    start_time,
                    format='long',
                    locale='fr'
                ),
                'START_TIME': start_time.strftime('%-Hh%M'),
                'END_TIME': end_time.strftime('%-Hh%M'),
                'HOURS_BEFORE_EMERGENCY':
                    settings.NUMBER_OF_DAYS_BEFORE_EMERGENCY_CANCELLATION * 24,

                'NUMBER_OF_VOLUNTEERS': updated_volunteer_count,
                'NUMBER_OF_VOLUNTEERS_NEEDED': self.event.nb_volunteers_needed,
                'NUMBER_OF_VOLUNTEERS_STANDBY':
                    self.event.nb_volunteers_standby,
                'NUMBER_OF_VOLUNTEERS_STANDBY_NEEDED':
                    self.event.nb_volunteers_standby_needed,
            },
            'CELL': {
                'NAME': self.event.cell.name,
                'ADDRESS_LINE_1': self.event.cell.address_line_1,
                'ADDRESS_LINE_2': self.event.cell.address_line_2,
                'POSTAL_CODE': self.event.cell.postal_code,
                'CITY': self.event.cell.city,
                'STATE_PROVINCE': self.event.cell.state_province,
            },
        }

        TEMPLATES = settings.ANYMAIL.get('TEMPLATES')
        id = TEMPLATES.get('CANCELLATION_PARTICIPATION_EMERGENCY')
        if id:
            EmailAPI().send_template_email(
                settings.LOCAL_SETTINGS['CONTACT_EMAIL'],
                'CANCELLATION_PARTICIPATION_EMERGENCY',
                context,
            )
        else:
            msg_file_name = 'participation_cancellation_email'
            plain_msg = render_to_string(
                '.'.join([msg_file_name, 'txt']),
                context
            )
            msg_html = render_to_string(
                '.'.join([msg_file_name, 'html']),
                context
            )
            EmailAPI().send_email(
                "Objet: Annulation de participation",
                plain_msg,
                "email_from@mondomain.ca",
                [settings.LOCAL_SETTINGS['CONTACT_EMAIL']],
                html_message=msg_html,
            )

    @staticmethod
    def has_destroy_permission(request):
        if request.user.is_staff:
            return True
        else:
            return False

    @staticmethod
    def has_update_permission(request):
        if request.user.is_staff:
            return True
        else:
            return False

    @staticmethod
    def has_list_permission(request):
        return True

    @staticmethod
    def has_create_permission(request):
        return True

    @authenticated_users
    def has_object_update_permission(self, request):
        if self.user == request.user:
            return True
        if request.user.is_staff:
            return True
        else:
            return False

    @authenticated_users
    def has_object_destroy_permission(self, request):
        if self.user == request.user:
            return True
        if request.user.is_staff:
            return True
        else:
            return False


@receiver(post_save, sender=Participation)
def send_participation_confirmation(sender, instance, created, **kwargs):
    if created:
        instance.send_email_confirmation()


@receiver(pre_delete, sender=Participation)
def send_cancellation_email_emergency(sender, instance, using, **kwargs):
    if not instance.is_standby:
        start_time = instance.event.start_time
        start_time = start_time.astimezone(pytz.timezone('US/Eastern'))
        limit_date = start_time - timedelta(
            days=settings.NUMBER_OF_DAYS_BEFORE_EMERGENCY_CANCELLATION
        )

        now = datetime.now(pytz.timezone('US/Eastern'))
        if now >= limit_date:
            instance.send_email_cancellation_emergency()
