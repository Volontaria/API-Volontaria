# coding: utf-8

from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token
from django.conf import settings


class TemporaryToken(Token):
    """Subclass of Token to add an expiration time."""
    expires = models.DateTimeField(
        default=timezone.now() + timezone.timedelta(
            minutes=settings.REST_FRAMEWORK_TEMPORARY_TOKENS['MINUTES']
        )
    )

    @property
    def expired(self):
        """Returns a boolean indicating token expiration."""
        return self.expires <= timezone.now()

    def expire(self):
        """Expires a token by setting its expiration date to now."""
        self.expires = timezone.now()
        self.save()
