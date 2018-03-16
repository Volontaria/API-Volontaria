import re

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, password_validation

from django.core import exceptions

from .models import ActivationToken, Profile


# Validator for phone numbers
def phone_number(phone):
    reg = re.compile('^(\+\d{1,2})?\d{9,10}$')
    char_list = " -.()"
    for i in char_list:
        phone = phone.replace(i, '')
    if not reg.match(phone):
        raise serializers.ValidationError("Invalid format.")


class AuthCustomTokenSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        login = attrs.get('login')
        password = attrs.get('password')

        if login and password:
            try:
                user_obj = User.objects.get(email=login)
                if user_obj:
                    login = user_obj.username
            except User.DoesNotExist:
                pass

            user = authenticate(request=self.context.get('request'),
                                username=login, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "login" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user

        return attrs


class UserBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_superuser',
            'password',
            'new_password',
            'phone',
            'mobile',
        )
        write_only_fields = (
            'password',
            'new_password',
        )
        read_only_fields = (
            'is_staff',
            'is_superuser',
            'is_active',
            'date_joined',
        )

    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message=_(
                    "An account for the specified email "
                    "address already exists."
                ),
            ),
        ],
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=False, write_only=True)

    phone = serializers.CharField(
        source='profile.phone',
        required=False,
        validators=[phone_number],
    )
    mobile = serializers.CharField(
        source='profile.mobile',
        required=False,
        validators=[phone_number],
    )

    def create(self, validated_data):
        try:
            password_validation.validate_password(
                password=validated_data['password']
            )
        except ValidationError as err:
            raise serializers.ValidationError({
                "password": err.messages
                })

        profile_data = None
        error_profile = False
        if 'profile' in validated_data.keys():
            profile_data = validated_data.pop('profile')

            if 'mobile' not in profile_data \
                    and 'phone' not in profile_data:
                error_profile = True
        else:
            error_profile = True

        if error_profile:
            raise serializers.ValidationError({
                "non_field_errors": [
                    'You must specify "phone" or "mobile" field.'
                ],
            })

        user = User(**validated_data)

        # Hash the user's password
        user.set_password(validated_data['password'])

        # Put user inactive by default
        user.is_active = False

        user.save()

        if profile_data:
            Profile.objects.create(
                user=user,
                **profile_data
            )

        # Create an ActivationToken to activate user in the future
        ActivationToken.objects.create(user=user)

        return user

    def update(self, instance, validated_data):
        if 'new_password' in validated_data.keys():
            try:
                old_pw = validated_data.pop('password')
            except KeyError:
                raise serializers.ValidationError(
                    'Missing "password" field. Cannot update password.'
                )
            new_pw = validated_data.pop('new_password')

            if instance.check_password(old_pw):
                try:
                    password_validation.validate_password(password=new_pw)
                except ValidationError as err:
                    raise serializers.ValidationError({
                        "password": err.messages
                        })
                instance.set_password(new_pw)
            else:
                msg = "Bad password"
                raise serializers.ValidationError(msg)

        if 'profile' in validated_data.keys():
            profile_data = validated_data.pop('profile')
            profile = Profile.objects.get_or_create(user=instance)
            profile[0].__dict__.update(profile_data)
            profile[0].save()

        return super(
            UserBasicSerializer,
            self
        ).update(instance, validated_data)


class UserPublicSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
        )
        read_only_fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
        )
