import re

from rest_framework import serializers

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from django.core import exceptions

from .models import ActivationToken, Profile


class AuthCustomTokenSerializer(serializers.Serializer):
    login = serializers.CharField()

    password = serializers.CharField()

    def validate_email(self, email):
        if len(email) > 6:
            if re.match(
                    '[A-Za-z0-1\.-]+'
                    '@[A-Za-z0-1\.-]+'
                    '\.[A-Za-z0-1]{2,4}',
                    email
            ):
                return 1
        return 0

    def validate(self, attrs):
        email_or_username = attrs.get('login')
        password = attrs.get('password')

        if email_or_username and password:
            # Check if user sent email
            if self.validate_email(email_or_username):
                email_exist = User.objects.filter(
                    email=email_or_username,
                )

                if not email_exist.count():
                    # Email is not use
                    msg = "This email doesn't have account"
                    raise exceptions.ValidationError(msg)

                email_or_username = email_exist[0].username
            else:
                user_exist = User.objects.filter(
                    username=email_or_username
                ).count()

                if not user_exist:
                    # User doesn't exist
                    msg = "This username doesn't have account"
                    raise exceptions.ValidationError(msg)

            user = authenticate(
                username=email_or_username,
                password=password
            )

            if user:
                if not user.is_active:
                    # User is inactive
                    msg = "This user is inactive"
                    raise exceptions.ValidationError(msg)
            else:
                # Bad password
                msg = "Bad password"
                raise exceptions.ValidationError(msg)

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
            'password',
            'phone',
            'mobile',
        )
        read_only_fields = [
            'id',
        ]

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    phone = serializers.CharField(
        source='profile.phone',
        required=False,
    )
    mobile = serializers.CharField(
        source='profile.mobile',
        required=False,
    )

    def create(self, validated_data):
        profile_data = None
        if 'profile' in validated_data.keys():
            profile_data = validated_data.pop('profile')

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
