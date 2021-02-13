import json

from datetime import timedelta
# from unittest import mock

from django.urls import reverse
from django.test.utils import override_settings
from django.contrib.auth import get_user_model
from django.contrib.admin import site

from rest_framework import status
from rest_framework.test import APIClient #, APITestCase
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.exceptions import ValidationError

from api_volontaria.factories import UserFactory, AdminFactory
from ..models import ActionToken
from ....testClasses import CustomAPITestCase

# from ..models import  APITokenProxy
from ..models import APIToken
from ..admin import APITokenAdmin

User = get_user_model()

class APITokenTests(CustomAPITestCase):
    """ 
    similar to AuthTokenTests class in django-rest-framework tests
    """

    ATTRIBUTES = [
        'is_staff',
        'last_login',
        'date_joined',
        'groups',
        'user_permissions',
        'url',
        'id',
        'is_superuser',
        'last_name',
        'is_active',
        'first_name',
        'permissions',
        'email'
    ]

    def setUp(self):
        self.site = site
        # self.client = APIClient()
        # self.user = UserFactory()
        self.user = AdminFactory()
        # self.user.set_password('Test123!')
        # self.user.save()
        self.token = APIToken.objects.create(key='test token', user=self.user)

    def test_model_admin_displayed_fields(self):
        mock_request = object()
        token_admin = APITokenAdmin(self.token, self.site)
        assert token_admin.get_fields(mock_request) == ('user',)

    def test_token_string_representation(self):
        assert str(self.token) == 'test token'
    
    def test_validate_raise_error_if_no_credentials_provided(self):
        with self.assertRaises(ValidationError):
            AuthTokenSerializer().validate({})
