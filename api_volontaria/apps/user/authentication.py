from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from .models import TemporaryToken


class TemporaryTokenAuthentication(TokenAuthentication):
    """
    Extends default token auth to handle temporary tokens.
    """
    models = TemporaryToken

    def authenticate_credentials(self, key):
        """
        Attempt token authentication using the provided key.
        """
        try:
            token = self.models.objects.get(key=key)
        except self.models.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(
                _('User inactive or deleted')
            )

        if token.expired:
            raise exceptions.AuthenticationFailed(_('Token has expired'))

        if settings.REST_FRAMEWORK_TEMPORARY_TOKENS['RENEW_ON_SUCCESS']:
            # Reset the token expiration time on successful authentication
            expires = timezone.now() + timezone.timedelta(
                minutes=settings.REST_FRAMEWORK_TEMPORARY_TOKENS['MINUTES']
            )
            token.expires = expires
            token.save()

        return token.user, token
