# coding: utf-8

from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token
from django.conf import settings


class TemporaryToken(Token):
    """Subclass of Token to add an expiration time."""
    expires = models.DateTimeField(
        verbose_name="Expiration date",
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.expires = timezone.now() + timezone.timedelta(
                minutes=settings.REST_FRAMEWORK_TEMPORARY_TOKENS['MINUTES']
            )

        super(TemporaryToken, self).save(*args, **kwargs)

    @property
    def expired(self):
        """Returns a boolean indicating token expiration."""
        return self.expires <= timezone.now()

    def expire(self):
        """Expires a token by setting its expiration date to now."""
        self.expires = timezone.now()
        self.save()
