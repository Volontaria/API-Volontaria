from datetime import datetime, timedelta
import pytz
from babel.dates import format_date
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from dry_rest_permissions.generics import authenticated_users
# from api_volontaria.email import EmailAPI

User = get_user_model()


class Position(models.Model):
    """
    This class represents a position that an organization can advertise and that volunteer can apply to.
    """

    class Meta:
        verbose_name = _("Position")
        verbose_name_plural = _("Positions")

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=100,
    )

    description = models.TextField(
        verbose_name="Description",
    )

    hourly_wage = models.FloatField(
        verbose_name=_("Hourly wage"),
    )
    
    weekly_hours = models.FloatField(
        verbose_name=_("Hourly wage"),
    )
    
    minimum_duration_commitment = models.FloatField(
        verbose_name=_("Minimum duration commitment"),
    )

    is_remote_job = models.BooleanField(
        verbose_name=_("Job is remote ")
    )
    
    is_posted = models.BooleanField(
        verbose_name=_("Is posted")
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


class Application(models.Model):
    """
    This class represents a application made by volunteer for a given position.
    """

    APPLICATION_UNDER_EXAMINATION = 'UNDER EXAMINATION'
    APPLICATION_ACCEPTED = 'ACCEPTED'
    APPLICATION_DECLINED = 'DECLINED'

    APPLICATION_CHOICES = (
        (APPLICATION_UNDER_EXAMINATION, _('Under examination')),
        (APPLICATION_ACCEPTED, _('Accepted')),
        (APPLICATION_DECLINED, _('Declined')),
    )

    class Meta:
        verbose_name = _("Application")
        verbose_name_plural = _("Applications")

    position = models.ForeignKey(
        Position,
        verbose_name=_("Position"),
        blank=False,
        on_delete=models.CASCADE,
    )
    
    applied_on = models.DateTimeField(
        verbose_name=_("Applied on"),
        auto_now_add=True,
    )
    
    motivation = models.TextField(
        verbose_name="Motivation",
    )

    application_status = models.CharField(
        verbose_name=_("Application status"),
        max_length=100,
        choices=APPLICATION_CHOICES,
        default=APPLICATION_UNDER_EXAMINATION
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