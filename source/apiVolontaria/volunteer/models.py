from django.contrib.auth.models import User
from django.db import models, IntegrityError
from django.utils import timezone

from location.models import Address


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

    @property
    def is_active(self):
        now = timezone.now()
        # Cycle is active if it has not ended yet (even if it has not started)
        if self.start_date and self.end_date:
            return self.end_date > now
        # Without date, the cycle is active
        return True


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


class Participation(models.Model):
    """

    This class represents the Participation model.

    A Participation object is used to join Users and Events together
    (M2M relationship) and store informations concerning that association.

    """

    class Meta:
        verbose_name_plural = 'Participations'
        unique_together = ('event', 'user')

    event = models.ForeignKey(Event, related_name='participation')
    user = models.ForeignKey(User, related_name='participation')

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
