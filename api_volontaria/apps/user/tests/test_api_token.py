import json

from datetime import timedelta
# from unittest import mock

from django.urls import reverse
from django.test.utils import override_settings
from django.contrib.auth import get_user_model
from django.contrib.admin import site

from rest_framework import status
# from rest_framework.test import APIClient #, APITestCase
# from rest_framework.authtoken.serializers import AuthTokenSerializer
# from rest_framework.exceptions import ValidationError

from api_volontaria.factories import UserFactory, AdminFactory
from ..models import ActionToken
from ....testClasses import CustomAPITestCase

# from ..models import  APITokenProxy
from ..models import APIToken
from ..admin import APITokenAdmin

# User = get_user_model()


class AuthAPITokenTests(CustomAPITestCase):
    """ 
    inspired by AuthTokenTests class in django-rest-framework tests
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
        self.user = UserFactory()
        self.admin = AdminFactory()
        # self.user.set_password('Test123!')
        # self.user.save()
        self.token = APIToken.objects.create(key='test token', user=self.admin)

    def test_model_admin_displayed_fields(self):
        mock_request = object()
        token_admin = APITokenAdmin(self.token, self.site)
        assert token_admin.get_fields(mock_request) == ('user', 'purpose')

    def test_token_string_representation(self):
        assert str(self.token) == 'test token'
    
    # TODO: confirm that we do not need to create a custom serializer for APIToken
    # def test_validate_raise_error_if_no_credentials_provided(self):
    #     with self.assertRaises(ValidationError):
    #         AuthTokenSerializer().validate({})
  
    def test_more_than_one_token_can_be_created_for_single_admin(self):
        
        token_initial_count = APIToken.objects.filter(
            user=self.admin
        ).count()

        self.token_2 = APIToken.objects.create(
            key='test token 2', user=self.admin
        )  

        token_final_count = APIToken.objects.filter(
            user=self.admin,
        ).count()

        self.assertEqual(token_final_count, token_initial_count + 1)           

    def test_token_can_be_created_through_django_admin_panel(self):
        # fails!!!!
        
        self.client.force_authenticate(user=self.admin)

        add_url = 'admin/user/apitoken/add/'

        data_post = {'user': self.admin.email}
        
        print(self.admin)
        print(self.admin.email)
        print(self.admin.id)
        print(self.admin.last_name)

        response = self.client.post(
            add_url,
            data_post,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.check_attributes(content)

    # TODO: we do not need to test that simple user cannot create tokens
    # since there is no url page that exposes token creation to user, right?
    # def test_create_new_token(self):
    #     """
    #     Ensure we can't create a new token if we are a simple user.
    #     """
    #     self.client.force_authenticate(user=self.user)
        
    #     data_post = {
    #         "user": self.user,
    #     }

    #     response = self.client.post(
    #         # reverse('position-list'), # no such url so ok, right
    #         data_post,
    #         format='json',
    #     )

    #     content = json.loads(response.content)

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.check_attributes(content)
