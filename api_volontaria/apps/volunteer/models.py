from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from dry_rest_permissions.generics import authenticated_users

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
