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
    # either email "subject" when using django_send_email
    # function via send_email or template key in ANYMAIL settings

    template_id = models.CharField(
        max_length=1024,
        verbose_name=_("Template ID"),
        null=True,
        blank=True,
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

    def __repr__(self):
        return str({
            'user_email': self.user_email,
            'type_email': self.type_email,
            'nb_email_sent': self.nb_email_sent,
            'template_id': self.template_id,
            'created': self.created,
        })

    @classmethod
    def add(cls, user_email, type_email, nb_email_sent, template_id=None):

        new_email_log = cls.objects.create(
            user_email=user_email,
            type_email=type_email,
            nb_email_sent=nb_email_sent,
            template_id=template_id
        )

        return new_email_log
