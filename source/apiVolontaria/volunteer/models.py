# -*- coding: utf-8 -*-

from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models, IntegrityError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from location.models import Address

from .managers import CycleManager


class Cycle(models.Model):

    class Meta:
        verbose_name_plural = 'Cycles'

    name = models.CharField(
        verbose_name="Name",
        max_length=100,
    )

    start_date = models.DateTimeField(
        verbose_name="Start date",
        blank=True,
        null=True
    )

    end_date = models.DateTimeField(
        verbose_name="End date",
        blank=True,
        null=True
    )

    objects = CycleManager()

    @property
    def is_active(self):
        now = timezone.now()
        # Cycle is active if it has not ended yet (even if it has not started)
        if self.start_date and self.end_date:
            return self.end_date > now
        # Without date, the cycle is active
        return True

    def __str__(self):
        return '{}'.format(self.name)

    def generate_participation_report_data(self):
        """
        This function will take all the Participations generated from
        this cycle and compile the time of every volunteer that has
        participated
        :return: This will return dict like this example :
        {
            1:{
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john.smith@gmail.com',
                'total_time': 300,
            },
            ...
        }
        """

        # Select all the Event of this Cycle
        events_in_cycle = Event.objects.filter(cycle=self)

        # Select all the participation of this Cycle
        participations = Participation.objects.filter(
            event__in=events_in_cycle,
        )

        data_dict = dict()

        for obj in participations:
            # We don't want to generate report
            # if some Participation are not initialised...
            # There is a message in the admin for this case
            if obj.presence_status == Participation.PRESENCE_STATUS[0][0]:
                return {'error': _("All of the Participations presence "
                        "status must be initialised.")}

            # The status is present so we compute it in the report
            if obj.presence_status == Participation.PRESENCE_STATUS[2][0]:
                min_duration = int(obj.duration.total_seconds() / 60)

                if obj.user.pk in data_dict:
                    data_dict[obj.user.pk]['total_time'] += min_duration
                else:
                    dataline = {
                        'first_name': obj.user.first_name,
                        'last_name': obj.user.last_name,
                        'email': obj.user.email,
                        'total_time': min_duration,
                    }
                    data_dict[obj.user.pk] = dataline

        return data_dict


class TaskType(models.Model):

    """

    This class represents the TaskType model.

    """

    class Meta:

        """

        This class represents the TaskType model's metadata.

        """

        verbose_name_plural = 'TaskTypes'

    name = models.CharField(
        verbose_name="Name",
        max_length=100,
    )

    def __str__(self):
        return '{}'.format(self.name)


class Cell(models.Model):
    """

    This class represents the Cell model.

    """
    class Meta:
        verbose_name_plural = 'Cells'

    name = models.CharField(
        verbose_name="Name",
        max_length=100,
    )

    address = models.ForeignKey(Address, blank=False)

    managers = models.ManyToManyField(
        User,
        verbose_name="Managers",
        related_name="managed_cell",
        blank=True,
    )

    def clean(self):
        if not self.name:
            raise IntegrityError("The Cell name cannot be empty.")

    def save(self, *args, **kwargs):
        self.clean()
        super(Cell, self).save(*args, **kwargs)

    def __str__(self):
        return '{}, {}'.format(self.name, str(self.address))


class Event(models.Model):
    """

    This class represents the Event model.

    """
    class Meta:
        verbose_name_plural = 'Events'
        ordering = ('start_date',)

    start_date = models.DateTimeField(
        verbose_name="Begin date",
        blank=False,
        null=False,
    )

    end_date = models.DateTimeField(
        verbose_name="End date",
        blank=False,
        null=False,
    )

    nb_volunteers_needed = models.PositiveIntegerField(
        verbose_name="Number of volunteers (needed)",
        default=0,
    )
    nb_volunteers_standby_needed = models.PositiveIntegerField(
        verbose_name="Number of volunteers on hold (needed)",
        default=0,
    )

    volunteers = models.ManyToManyField(
        User,
        verbose_name="Volunteers",
        related_name="events",
        blank=True,
        through='Participation',
    )

    cell = models.ForeignKey(
        Cell,
        verbose_name="Cell",
        blank=False,
    )

    cycle = models.ForeignKey(
        Cycle,
        verbose_name="Cycle",
        blank=False,
    )

    task_type = models.ForeignKey(
        TaskType,
        verbose_name="Task type",
        blank=False,
    )

    def clean(self):
        if self.start_date and self.end_date:

            if self.start_date > self.end_date:
                error = "The start date needs to be older than end date."
                raise IntegrityError(error)

            cycle = None
            try:
                cycle = self.cycle
            except Exception:
                pass

            if cycle:
                if cycle.start_date and cycle.start_date > self.start_date:
                    error = "The start date can't be older than " \
                            "start date of the cycle."
                    raise IntegrityError(error)

                if cycle.end_date and cycle.end_date < self.end_date:
                    error = "The end date can't be younger than " \
                            "end date of the cycle."
                    raise IntegrityError(error)

    def save(self, *args, **kwargs):
        self.clean()
        super(Event, self).save(*args, **kwargs)

    def __str__(self):
        return '{0}, {1}, {2}, {3} - {4}'.format(
            self.cell,
            self.cycle,
            self.task_type,
            str(self.start_date),
            str(self.end_date),
        )

    @property
    def is_started(self):
        return self.start_date <= timezone.now()

    @property
    def is_expired(self):
        return self.end_date <= timezone.now()

    @property
    def is_active(self):
        return self.cycle.is_active

    @property
    def nb_volunteers(self):
        return self.volunteers.filter(participation__standby=False).count()

    @property
    def nb_volunteers_standby(self):
        return self.volunteers.filter(participation__standby=True).count()

    @property
    def duration(self):
        return self.end_date - self.start_date


class Participation(models.Model):
    """

    This class represents the Participation model.

    A Participation object is used to join Users and Events together
    (M2M relationship) and store informations concerning that association.

    """
    PRESENCE_STATUS = (
        ('I', _('Initialisation')),
        ('A', _('Absent')),
        ('P', _('Present')),
    )

    class Meta:
        verbose_name_plural = 'Participations'
        unique_together = ('event', 'user')

    event = models.ForeignKey(Event, related_name='participation')
    user = models.ForeignKey(User, related_name='participation')

    presence_duration_minutes = models.PositiveIntegerField(
        default=None,
        blank=True,
        null=True
    )

    presence_status = models.CharField(
        max_length=1,
        choices=PRESENCE_STATUS,
        default=PRESENCE_STATUS[0][0]
    )

    standby = models.BooleanField(
        verbose_name="Standby",
    )

    subscription_date = models.DateTimeField(
        verbose_name="Subscription date",
        auto_now=True,
    )

    def __str__(self):
        return '{0}, {1}, {2}, {3}'.format(
            self.user,
            self.event,
            self.standby,
            str(self.subscription_date),
        )

    @property
    def start_date(self):
        return self.event.start_date

    @property
    def end_date(self):
        return self.event.end_date

    @property
    def cell(self):
        return self.event.cell.name

    @property
    def duration(self):
        if self.presence_duration_minutes:
            return timedelta(minutes=self.presence_duration_minutes)
        else:
            return self.event.duration
