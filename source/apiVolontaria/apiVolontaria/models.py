# coding: utf-8
import binascii
import os
import re

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token

# Make the "email" field of users unique in the database
# Implemented in custom migration "9999_user_email_unique.py"
User._meta.get_field('email')._unique = True


class ActivationToken(models.Model):
    """Class of Token to allow User to activate his account."""

    key = models.CharField(
        verbose_name="Key",
        max_length=40,
        primary_key=True
    )

    user = models.OneToOneField(
        User,
        related_name='activation_token',
        on_delete=models.CASCADE,
        verbose_name="User"
    )

    created = models.DateTimeField(
        verbose_name="Creation date",
        auto_now_add=True
    )

    expires = models.DateTimeField(
        verbose_name="Expiration date",
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
            self.expires = timezone.now() + timezone.timedelta(
                minutes=settings.ACTIVATION_TOKENS['MINUTES']
            )
        return super(ActivationToken, self).save(*args, **kwargs)

    @staticmethod
    def generate_key():
        """Generate a new key"""
        return binascii.hexlify(os.urandom(20)).decode()

    @property
    def expired(self):
        """Returns a boolean indicating token expiration."""
        return self.expires <= timezone.now()

    def expire(self):
        """Expires a token by setting its expiration date to now."""
        self.expires = timezone.now()
        self.save()

    def __str__(self):
        return self.key


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


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    phone = models.CharField(
        verbose_name="Phone number",
        blank=True,
        null=True,
        max_length=17,
    )
    mobile = models.CharField(
        verbose_name="Mobile number",
        blank=True,
        null=True,
        max_length=17,
    )

    def clean(self):
        reg = re.compile('^(\+\d{1,2})?\d{9,10}$')
        if self.phone:
            self.phone = self.phone\
                .replace(" ", "")\
                .replace("-", "")\
                .replace(".", "")\
                .replace("(", "")\
                .replace(")", "")
            if not reg.match(self.phone):
                raise ValidationError(
                    'The phone field need to be in a valid format'
                )
        if self.mobile:
            self.mobile = self.mobile\
                .replace(" ", "")\
                .replace("-", "")\
                .replace(".", "")\
                .replace("(", "")\
                .replace(")", "")
            if not reg.match(self.mobile):
                raise ValidationError(
                    'The mobile field need to be in a valid format'
                )

    def save(self, *args, **kwargs):
        self.clean()
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user)
