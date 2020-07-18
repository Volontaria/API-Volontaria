import json
import traceback

from django.db import models

from django.utils.translation import ugettext_lazy as _


class Log(models.Model):

    LEVEL_ERROR = 'ERROR'
    LEVEL_INFO = 'INFO'
    LEVEL_DEBUG = 'DEBUG'

    source = models.CharField(
        max_length=100,
        verbose_name=_("Source"),
    )

    level = models.CharField(
        max_length=100,
        verbose_name=_("Level"),
    )

    message = models.TextField(
        verbose_name=_("Message"),
    )

    error_code = models.CharField(
        blank=True,
        null=True,
        max_length=100,
        verbose_name=_("Error Code"),
    )

    additional_data = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Additional data"),
    )

    traceback_data = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("TraceBack"),
    )
    created = models.DateTimeField(
        verbose_name="Creation date",
        auto_now_add=True,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Log")
        verbose_name_plural = _("Logs")

    @classmethod
    def error(cls, source, message, error_code=None, additional_data=None):
        traceback_data = ''.join(traceback.format_stack(limit=10))
        new_log = Log(
            level=cls.LEVEL_ERROR,
            source=source,
            message=message,
            traceback_data=traceback_data
        )

        if error_code:
            new_log.error_code = error_code
        if additional_data:
            new_log.additional_data = additional_data

        new_log.save()

        return new_log


class EmailLog(models.Model):

    user_email = models.CharField(
        max_length=1024,
        verbose_name=_("User email")
    )

    type_email = models.CharField(
        max_length=1024,
        verbose_name=_("Type email")
    )

    nb_email_sent = models.IntegerField(
        verbose_name=_("Number email sent")
    )

    created = models.DateTimeField(
        verbose_name="Creation date",
        auto_now_add=True
    )

    class Meta:
        verbose_name = _("Email Log")
        verbose_name_plural = _("Email Logs")

    @classmethod
    def add(cls, user_email, type_email, nb_email_sent):

        new_email_log = cls.objects.create(
            user_email=user_email,
            type_email=type_email,
            nb_email_sent=nb_email_sent
        )

        return new_email_log
