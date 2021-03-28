import binascii
import os

from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils.translation import ugettext_lazy as _

from api_volontaria.apps.user.managers import UserManager, ActionTokenManager
# from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string


class User(AbstractUser):
    """Abstraction of the base User model. Needed to extend in the future."""

    username = None
    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def display_name(self):
        return f'{self.first_name} {self.last_name}' \
            if self.first_name and self.last_name \
            else self.email

    @staticmethod
    def create(email, password, validated_data):
        print(email)
        print(password)
        print(validated_data)
        user, created = User.objects.get_or_create(
            email=email,
            defaults=validated_data
        )

        # Hash the user's password
        user.set_password(password)
        # Put user inactive by default
        user.is_active = False
        user.save()

        # Create an ActivationToken to activate user in the future
        ActionToken.objects.create(
            user=user,
            type='account_activation',
        )

        return user


class ActionToken(models.Model):
    """
        Class of Token to allow User to do some action.

        Generally, the token is sent by email and serves
        as a "right" to do a specific action.
    """

    ACTIONS_TYPE = [
        ('account_activation', _('Account activation')),
        ('password_change', _('Password change')),
    ]

    key = models.CharField(
        verbose_name="Key",
        max_length=40,
        primary_key=True
    )

    type = models.CharField(
        verbose_name='Type of action',
        max_length=100,
        choices=ACTIONS_TYPE,
        null=False,
    )

    user = models.ForeignKey(
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

    objects = ActionTokenManager()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
            self.expires = timezone.now() + timezone.timedelta(
                minutes=settings.ACTIVATION_TOKENS['MINUTES']
            )
        return super(ActionToken, self).save(*args, **kwargs)

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

    @staticmethod
    def generate_activation_url(user: User):
        # Get the token of the saved user and send it with an email
        activate_token = ActionToken.objects.get(
            user=user,
            type='account_activation',
        )

        return activate_token.get_url()

    @staticmethod
    def generate_reset_password_url(user: User):
        # remove old tokens to change password
        tokens = ActionToken.objects.filter(
            type='password_change',
            user=user,
        )

        for token in tokens:
            token.expire()

        # Get the token of the saved user and send it with an email
        activate_token = ActionToken.objects.create(
            user=user,
            type='password_change',
        )

        return activate_token.get_url()

    def get_url(self):

        FRONTEND_SETTINGS = settings.LOCAL_SETTINGS[
            'FRONTEND_INTEGRATION'
        ]
        # Setup the url for the activation button in the email
        activation_url = FRONTEND_SETTINGS['ACTIVATION_URL'].replace(
            "{{token}}",
            self.key
        )

        return activation_url

    @staticmethod
    def get_password_change_token(token_key):
        return ActionToken.objects.get(
            key=token_key,
            type='password_change',
            expired=False,
        )


class Address(models.Model):
    """Abstract model for address"""
    country = models.CharField(
        max_length=45,
        blank=False,
        verbose_name=_("Country"),
    )

    state_province = models.CharField(
        max_length=55,
        blank=False,
        verbose_name=_("State/Province"),
    )
    city = models.CharField(
        max_length=50,
        blank=False,
        verbose_name=_("City"),
    )
    address_line1 = models.CharField(
        max_length=45,
        verbose_name=_("Address line 1"),
    )
    address_line2 = models.CharField(
        max_length=45,
        blank=True,
        default='',
        verbose_name=_("Address line 2"),
    )
    postal_code = models.CharField(
        max_length=10,
        verbose_name=_("Postal code"),
    )
    latitude = models.FloatField(
        blank=True,
        null=True,
        verbose_name=_("Latitude"),
    )
    longitude = models.FloatField(
        blank=True,
        null=True,
        verbose_name=_("Longitude"),
    )
    timezone = models.CharField(
        blank=True,
        null=True,
        max_length=100,
        verbose_name=_("Timezone"),
    )

    class Meta:
        abstract = True


class APIToken(models.Model):
    """
    A model allowing for multiple persistent tokens per single user,
    each for a different purpose
    """

    # The token key must not be the primary key, 
    # because django admin displays the primary key in the url address bar!
    # (for reference, DRF, where the token is the primary key, needs an APIProxy class)
    key = models.CharField(_("Key"), max_length=40, unique=True) 
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='api_token',
        on_delete=models.CASCADE, verbose_name=_("User")
    )
    purpose = models.CharField(_("Purpose"), max_length=200, blank=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        # Work around for a bug in Django:
        # https://code.djangoproject.com/ticket/19422
        #
        # Also see corresponding ticket:
        # https://github.com/encode/django-rest-framework/issues/705
        abstract = 'rest_framework.authtoken' not in settings.INSTALLED_APPS
        verbose_name = _("API Token")
        verbose_name_plural = _("API Tokens")

        unique_together = [['user', 'purpose']]

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
