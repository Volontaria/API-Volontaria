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
from imailing.Mailing import IMailing


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
                error = _("Could not authenticate user.")
                return Response(
                    {'error': error},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Users(generics.ListCreateAPIView):
    """
    get:
    List all users in the system.

    post:
    Create a new user.
    """
    serializer_class = serializers.UserBasicSerializer

    def get_queryset(self):
        return User.objects.all()

    def get(self, request, *args, **kwargs):
        if self.request.user.has_perm('apiVolontaria.list_user'):
            return self.list(request, *args, **kwargs)

        content = {
            'detail': _("You are not authorized to list users."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = ()

        return [permission() for permission in self.permission_classes]

    def get_authenticators(self):
        if self.request.method == 'POST':
            self.authentication_classes = ()
        return [auth() for auth in self.authentication_classes]

    def post(self, request, *args, **kwargs):
        response = self.create(request, *args, **kwargs)
        # get token for user save and send key this token with a mail
        user = User.objects.get(username=request.data["username"])

        if response.status_code == status.HTTP_201_CREATED:
            if settings.CONSTANT['AUTO_ACTIVATE_USER'] is True:
                user.is_active = True
                user.save()

            if settings.CONSTANT['EMAIL_SERVICE'] is True:
                MAIL_SERVICE = settings.SETTINGS_IMAILING
                FRONTEND_SETTINGS = settings.CONSTANT['FRONTEND_INTEGRATION']

                # Get the token of the saved user and send it with an email
                activate_token = ActivationToken.objects.get(user=user).key

                # Setup the url for the activation button in the email
                activation_url = FRONTEND_SETTINGS['ACTIVATION_URL'].replace(
                    "{{token}}",
                    activate_token
                )

                # Send email with a SETTINGS_IMAILING
                email = IMailing.\
                    create_instance(MAIL_SERVICE["SERVICE"],
                                    MAIL_SERVICE["API_KEY"])
                response_send_mail = email.send_templated_email(
                    email_from=MAIL_SERVICE["EMAIL_FROM"],
                    template_id=MAIL_SERVICE["TEMPLATES"]["CONFIRM_SIGN_UP"],
                    list_to=[request.data["email"]],
                    context={
                        "activation_url": activation_url,
                        },
                )

                if response_send_mail["code"] == "failure":
                    content = {
                        'detail': _("The account was created but no email was "
                                    "sent. If your account is not "
                                    "activated, contact the administration."),
                    }
                    return Response(content, status=status.HTTP_201_CREATED)

        return response


class UsersId(generics.RetrieveUpdateAPIView):
    """
    get:
    Return the detail of a specific user.
    patch:
    Partially update a user.
    """
    serializer_class = serializers.UserBasicSerializer

    def get_queryset(self):
        return User.objects.filter()

    def get(self, request, *args, **kwargs):
        if 'profile' in self.kwargs.keys():
            self.kwargs['pk'] = self.request.user.id
            return self.retrieve(request, *args, **kwargs)

        elif self.request.user.has_perm('apiVolontaria.get_user'):
            return self.retrieve(request, *args, **kwargs)

        content = {
            'detail': _("You are not authorized to get "
                        "detail of a given user."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, *args, **kwargs):
        if 'profile' in self.kwargs.keys():
            self.kwargs['pk'] = self.request.user.id
            return self.partial_update(request, *args, **kwargs)

        elif self.request.user.has_perm('apiVolontaria.change_user'):
            return self.partial_update(request, *args, **kwargs)

        content = {
            'detail': _("You are not authorized to update a given user."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        content = {
            "detail": _("Method \"PUT\" not allowed.")
        }
        return Response(content, status=status.HTTP_405_METHOD_NOT_ALLOWED)


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
            error = _("The system have a problem, please contact us, "
                      "it is not your fault.")
            return Response(
                {'detail': error},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
