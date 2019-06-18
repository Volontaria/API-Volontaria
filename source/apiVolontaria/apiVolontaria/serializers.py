import re

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, password_validation

from coupons import wc_api
from coupons.models import RechargeableCoupon
from volunteer.models import Cell, Participation
from .models import ActionToken, Profile


# Validator for phone numbers
def phone_number(phone):
    reg = re.compile('^([+][0-9]{1,2})?[0-9]{9,10}$')
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
            'managed_cell',
            'coupon',
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
            'coupon',
        )

    coupon = serializers.SerializerMethodField()

    def get_coupon(self, obj):
        coupon = RechargeableCoupon.objects.filter(user=obj).first()
        serializer = RechargeableCouponBasicSerializer(instance=coupon, many=False)
        return serializer.data

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

    managed_cell = serializers.SerializerMethodField()

    # https://github.com/Volontaria/API-Volontaria/pull/222/

    phone = serializers.CharField(
        source='profile.phone',
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[phone_number],
    )
    mobile = serializers.CharField(
        source='profile.mobile',
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[phone_number],
    )

    def validate(self, attrs):
        mobile = self.initial_data.get('mobile', None)
        phone = self.initial_data.get('phone', None)

        if not mobile and not phone:
            raise serializers.ValidationError({
                "phone": [
                    _('You must specify "phone" or "mobile" field.')
                ],
                "mobile": [
                    _('You must specify "phone" or "mobile" field.')
                ],
            })

        return attrs

    def get_managed_cell(self, obj):
        cells = Cell.objects.filter(managers__in=[obj])

        # Need to import here because of circular / recursive import error
        from volunteer.serializers import CellBasicSerializer

        return CellBasicSerializer(cells, many=True, read_only=True).data

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
        if 'profile' in validated_data.keys():
            profile_data = validated_data.pop('profile')
        else:
            raise serializers.ValidationError({
                "non_field_errors": [
                    _('profile data missing.')
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

        # Create an ActionToken to activate user in the future
        ActionToken.objects.create(
            user=user,
            type='account_activation',
        )

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


class UserAdminSerializer(UserBasicSerializer):
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
            'managed_cell',
            'coupon',
            'volunteer_note',
            'last_participation'
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
            'coupon',
            'volunteer_note',
            'last_participation'
        )

    volunteer_note = serializers.SerializerMethodField()
    last_participation = serializers.SerializerMethodField()

    def get_volunteer_note(self, obj):
        try:
            return obj.profile.volunteer_note
        except:
            return ''

    def get_last_participation(self, obj):
        last_participation = Participation.objects.filter(user=obj, presence_status='P').order_by('-event__start_date').first()

        if last_participation:
            return last_participation.start_date

        return ''


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


class ResetPasswordSerializer(serializers.Serializer):

    username_email = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):

    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class RechargeableCouponBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = RechargeableCoupon
        fields = (
            'code',
            'balance',
        )
        read_only_fields = fields

    balance = serializers.SerializerMethodField()

    def get_balance(self, obj):
        API = wc_api.WooCommerceAPI()
        data = API.get_coupons(obj.coupon_wc_id)

        if data.status_code == 200:
            try:
                return '%s $' % str(data.json()['amount'])
            except:
                pass

        return "N/A"
