from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from rest_framework import generics, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from .models import TemporaryToken, ActivationToken


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


class UsersId(generics.RetrieveAPIView):
    """
    get:
    Return the detail of a specific user.
    """
    serializer_class = serializers.UserBasicSerializer

    def get_queryset(self):
        return User.objects.filter()

    def get(self, request, *args, **kwargs):
        if self.request.user.has_perm('apiVolontaria.get_user'):
            return self.retrieve(request, *args, **kwargs)

        content = {
            'detail': "You are not authorized to get detail of a given user.",
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)


class UsersActivation(APIView):
    """
    Activate user from an activation token
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.UserBasicSerializer

    def post(self, request):
        """
        Respond to POSTed username/password with token.
        """
        activation_token = request.data.get('activation_token')

        token = ActivationToken.objects.filter(key=activation_token)

        # There is only one reference, we will set the user active
        if len(token) == 1:
            # We activate the user
            user = token[0].user
            user.is_active = True
            user.save()

            # We delete the token used
            token[0].delete()

            # We return the user
            serializer = serializers.UserBasicSerializer(user)
            return Response(serializer.data)

        # There is no reference to this token
        elif len(token) == 0:
            error = '"{0}" is not a valid activation_token.'. \
                format(activation_token)

            return Response(
                {'detail': error},
                status=status.HTTP_400_BAD_REQUEST
            )
        # We have multiple token with the same key (impossible)
        else:
            error = 'The system have a problem, please contact us, ' \
                    'it is not your fault.'
            return Response(
                {'detail': error},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
