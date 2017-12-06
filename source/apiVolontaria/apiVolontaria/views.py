from django.contrib.auth import authenticate
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from rest_framework import generics, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from . import serializers
from .models import TemporaryToken


class ObtainTemporaryAuthToken(ObtainAuthToken):
    """
    Enables username/password exchange for expiring token.
    """
    model = TemporaryToken

    def post(self, request):
        """
        Respond to POSTed username/password with token.
        """
        serializer = serializers.AuthCustomTokenSerializer(data=request.data)

        CONFIG = settings.REST_FRAMEWORK_TEMPORARY_TOKENS

        if (serializer.is_valid() or (
                'USE_AUTHENTICATION_BACKENDS'
                in CONFIG and CONFIG['USE_AUTHENTICATION_BACKENDS'])):

            user = None
            try:
                user = serializer.validated_data['user']
            except KeyError:
                if ('email' in request.data and
                        'username' in request.data and
                        'password' in request.data):

                    user = authenticate(
                        email=request.data['email'],
                        username=request.data['username'],
                        password=request.data['password']
                    )

                elif ('email' in request.data and
                        'password' in request.data):

                    user = authenticate(
                        email=request.data['email'],
                        password=request.data['password']
                    )

            token = None
            if user:
                token, _created = TemporaryToken.objects.get_or_create(
                    user=user
                )

            if token and token.expired:
                # If the token is expired, generate a new one.
                token.delete()
                expires = timezone.now() + timezone.timedelta(
                    minutes=CONFIG['MINUTES']
                )

                token = TemporaryToken.objects.create(
                    user=user, expires=expires)

            if token:
                data = {'token': token.key}
                return Response(data)
            else:
                error = _('Could not authenticate user')
                return Response(
                    {'error': error},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Users(generics.CreateAPIView):
    """
    post:
    Create a new user.
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.UserBasicSerializer
