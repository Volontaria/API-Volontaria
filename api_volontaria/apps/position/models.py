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
from djmoney.models.fields import MoneyField

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
        verbose_name=_("Description"),
    )

    hourly_wage = MoneyField(
        verbose_name=_("Hourly wage"),
        max_digits=10,
        decimal_places=2,
        default_currency='CAD',
    )
    
    weekly_hours = models.FloatField(
        verbose_name=_("Weekly hours"),
    )
    
    minimum_days_commitment = models.FloatField(
        verbose_name=_("Minimum days commitment"),
    )

    is_remote_job = models.BooleanField(
        verbose_name=_("Is remote")
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
    This class represents an application made by volunteer for a given position.
    """

    APPLICATION_UNDER_EXAMINATION = 'UNDER_EXAMINATION'
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
        verbose_name=_("Motivation"),
    )

    application_status = models.CharField(
        verbose_name=_("Application status"),
        max_length=100,
        choices=APPLICATION_CHOICES,
        default=APPLICATION_UNDER_EXAMINATION
    )

    user = models.ForeignKey(
        User,
        related_name='applications',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.user

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
        if self.user == request.user and \
        self.application_status == APPLICATION_UNDER_EXAMINATION:
            return True
        if request.user.is_staff:
            return True
        else:
            return False

    @authenticated_users
    def has_object_destroy_permission(self, request):
        if self.user == request.user and \
        self.application_status == APPLICATION_UNDER_EXAMINATION:
            return True
        if request.user.is_staff:
            return True
        else:
            return False