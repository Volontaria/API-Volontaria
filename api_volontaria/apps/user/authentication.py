from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.authentication import get_authorization_header

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from .models import APIToken


class APITokenAuthentication(BaseAuthentication):
    
    """
    TokenAuthentication class, copied-pasted at 99% from django rest framwork:
    Simple token based authentication.
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "APIToken ".  For example:
        Authorization: APIToken 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = 'APIToken'
    model = APIToken

    def get_model(self):
        return self.model

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return (token.user, token)

    def authenticate_header(self, request):
        return self.keyword
