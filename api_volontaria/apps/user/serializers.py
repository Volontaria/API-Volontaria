from datetime import datetime
import re

from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth import authenticate
from django.db.models.fields import DurationField
from django.utils.translation import ugettext_lazy as _

from rest_framework.settings import api_settings

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from dry_rest_permissions.generics import DRYGlobalPermissionsField
from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.serializers import PasswordResetSerializer

from api_volontaria.apps.user.models import ActionToken
from api_volontaria.apps.user.models import APIToken

User = get_user_model()


class CustomRegisterSerializer(RegisterSerializer):

    first_name = serializers.CharField(
        max_length=30,
        allow_blank=True,
        allow_null=True,
        required=False
    )

    last_name = serializers.CharField(
        max_length=150,
        allow_blank=True,
        allow_null=True,
        required=False
    )

    password1 = serializers.CharField(write_only=True, required=False)
    password2 = serializers.CharField(write_only=True, required=False)

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
        }

    def validate(self, data):
        if 'password1' in data and data['password1'] != data['password2']:
            raise serializers.ValidationError(
                _("The two password didn't match."))

        return data


class CustomPasswordResetSerializer(PasswordResetSerializer):

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def save(self):

        try:
            from api_volontaria.apps.notification.models import Notification
            Notification.generate_reset_password(
                User.objects.get(
                    email=self.validated_data.get('email')
                )
            )
        except ObjectDoesNotExist:
            pass


class UserSerializer(serializers.HyperlinkedModelSerializer):

    id = serializers.ReadOnlyField()
    permissions = DRYGlobalPermissionsField()

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': False,
                'help_text': _("A valid password."),
            },
            'first_name': {
                'allow_blank': False,
                'help_text': _("A valid first name."),
            },
            'last_name': {
                'allow_blank': False,
                'help_text': _("A valid last name."),
            },
        }
        read_only_fields = (
            'id',
            'url',
            'is_staff',
            'is_superuser',
            'is_active',
            'date_joined',
            'last_login',
            'groups',
            'user_permissions',
            'email',
            'permissions'
        )


class UserLightSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id',
            'url',
            'first_name',
            'last_name',
            'email',
        ]
        read_only_fields = (
            'id',
            'url',
            'first_name',
            'last_name',
            'email',
        )


class APITokenSerializer(serializers.Serializer):
    ''' Class strongly inspired from AuthTokenSerializer class 
    in Django Rest Framework.
    One addition:
    - purpose

   '''

    class Meta:
       model = APIToken
       fields = [
           'email',
        #    'password',
            # 'user',
            'purpose',
            'token',
       ]

    #TODO: ask whether setup below is legit
    # email = serializers.EmailField(
    #     label=_("Email"),
    #     write_only=True
    # )

    # email = serializers.EmailField(
    #     source = 'user.email',
    #     label=_("Email"),
    #     read_only=True
    # )

    email = serializers.EmailField(
        source = 'user.email',
        label=_("Email"),
        # read_only=True
    )

    # password = serializers.CharField(
    #     label=_("Password"),
    #     style={'input_type': 'password'},
    #     trim_whitespace=False,
    #     write_only=True
    # )
    token = serializers.CharField(
        label=_("APIToken"),
        read_only=True
    )

    purpose = serializers.CharField(
        label=_("Purpose")
    )

    def validate(self, attrs):
        '''
        Validates whether user for whom token is meant exists.
        Since email is unique in User model
        but admin who creates tokens for other users
        does not know their password,
        we use email to access user
        and check that user is active
        (different approach from DRF Token
        where validation is with username + password,
        since, in DRF, users can only create tokens for themselves) 
        '''
        email = attrs.get('email')
        # password = attrs.get('password')

        if email:
            user = User.objects.get(email=email)
            print('user ***')
            print(user)
            print('*** user')
            print('active?')
            print(user.is_active)
            print('---')
            if not user.is_active:
                msg = _('Unable to create token for this user, \
                    as there is no active user \
                    with the "email" you provided.')

                raise serializers.ValidationError(msg)            
            # authenticate(request=self.context.get('request'),
            #                     username=username, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            # if not user:
            #     msg = _('Unable to log in with provided credentials.')
            #     raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" of the user for whom \
                you want to create a token')
            raise serializers.ValidationError(msg)

        attrs['user'] = user
        # attrs['email'] = email

        print('+++ attrs')
        print(attrs)
        print('++++')

        return attrs
