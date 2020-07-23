from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db import models
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from api_volontaria import front_end_url
from api_volontaria.email import EmailAPI

User = get_user_model()


class Notification(models.Model):
    notification_key = models.CharField(
        max_length=150,
        verbose_name=_('Notification Key')
    )

    email = models.CharField(
        verbose_name=_('Email user'),
        max_length=1024
    )

    notification_data = models.TextField(
        verbose_name=_('Notification Data'),
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        verbose_name=_('Creation Date'),
        auto_now_add=True
    )

    is_read = models.BooleanField(
        verbose_name=_('Is Read'),
        default=False
    )

    def __str__(self):
        return f'{self.email} - {self.notification_key}'

    def save(self, *args, **kwargs):
        send_email = self.pk is None
        super(Notification, self).save(*args, **kwargs)

        if send_email:
            self.send_email()

    def send_email(self):
        EmailAPI().send_template_email(
            self.email,
            self.notification_key,
            self.notification_data
        )

    @classmethod
    def generate_reset_password(
            cls, user):
        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_password_url = front_end_url.reset_password_url(
            token,
            uid
        )

        data = {
            "DISPLAY_NAME": user.display_name,
            "RESET_PASSWORD_URL": reset_password_url,
        }

        cls.objects.create(
            notification_key='RESET_PASSWORD',
            email=user.email,
            notification_data=data
        )
