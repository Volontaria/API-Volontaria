# Standard library
import json
from datetime import timedelta
from os import PRIO_PGRP

# Third-party libraries
from django.contrib.admin import site
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework.exceptions import ValidationError
from rest_framework import status

# Application modules
from api_volontaria.apps.user.serializers import SingleAPITokenSerializer
from api_volontaria.factories import UserFactory, AdminFactory
from ....testClasses import CustomAPITestCase
from ..models import APIToken
from ..admin import APITokenAdmin


class APITokenTests(CustomAPITestCase):
    """ 
    inspired from AuthTokenTests class in django-rest-framework tests
    """

    def setUp(self):
        self.site = site
        self.client = APIClient()
        self.user = UserFactory()
        self.user1 = UserFactory()
        self.admin = AdminFactory()
        self.user_authtoken = APIToken.objects.create(
            key='test_user_apitoken_123',
            user=self.user,
            purpose='Service alpha')
        self.user_authtoken2 = APIToken.objects.create(
            key='test_user_apitoken_456',
            user=self.user,
            purpose='Service beta',
            )
        self.admin_apitoken = APIToken.objects.create(
            key='test_admin_apitoken',
            user=self.admin,
            purpose='Service gamma')

    # Three generic tests strongly inspired 
    # from DRF testing suite for Token
    
    def test_model_admin_displayed_fields(self):
        mock_request = object()
        token_admin = APITokenAdmin(self.admin_apitoken, self.site)
        assert token_admin.get_fields(mock_request) == ('user', 'purpose')

    def test_token_string_representation(self):
        assert str(self.admin_apitoken) == 'test_admin_apitoken'
    
    def test_validate_raise_error_if_no_credentials_provided(self):
        with self.assertRaises(ValidationError):
            SingleAPITokenSerializer().validate({})


    # Tests tailored to Volontaria API Token
    # permission system:
    # Admin has all write and read permissions
    # Users can only list their own API Tokens (seeing purpose only)
      
    def test_more_than_one_token_can_be_created_for_single_admin(self):
        token_initial_count = APIToken.objects.filter(
            user=self.admin
        ).count()

        self.token_2 = APIToken.objects.create(
            key='test_admin_apitoken_2',
            user=self.admin, 
            purpose='Service zeta',
        )  

        token_final_count = APIToken.objects.filter(
            user=self.admin,
        ).count()

        self.assertEqual(token_final_count, token_initial_count + 1)

    def test_more_than_one_token_can_be_created_for_single_user(self):
        token_initial_count = APIToken.objects.filter(
            user=self.user
        ).count()

        self.token_2 = APIToken.objects.create(
            key='test_apitoken_2',
            user=self.user,
            purpose="Service gamma"
        )

        token_final_count = APIToken.objects.filter(
            user=self.user,
        ).count()

        self.assertEqual(token_final_count, token_initial_count + 1)

    def test_user_cannot_create_api_token(self):
        self.client.force_authenticate(user=self.user)

        data_post = {
            'purpose': 'New Service',
            'user_email': self.user.email,
        }

        # auth = self.header_prefix + self.key

        response = self.client.post(
            reverse('api-token-list'),
            data_post,
            format='json',
        )

        # self.client.post(
        #     reverse('application-list'),
        #     data_post,
        #     format='json',
        #     HTTP_AUTHORIZATION=auth,
        # )

        content = json.loads(response.content)

        print(content)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_admin_can_create_api_token_for_oneself(self):
        initial_api_token_count = APIToken.objects.filter(
            user=self.admin
        ).count()
        
        self.client.force_authenticate(user=self.admin)       

        data_post = {
            'purpose': 'New Service',
            'user_email': self.admin.email,
        }

        response = self.client.post(
            reverse('single-api-token-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        final_api_token_count = APIToken.objects.filter(
            user=self.admin
        ).count()

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            content
        )

        self.assertEqual(
            final_api_token_count,
            initial_api_token_count + 1
        )

    def test_admin_can_create_api_token_for_user(self):
        initial_api_token_count = APIToken.objects.filter(
            user=self.user
        ).count()
        
        self.client.force_authenticate(user=self.admin)       

        data_post = {
            'purpose': 'New Service',
            'user_email': self.user.email,
        }

        response = self.client.post(
            reverse('single-api-token-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        final_api_token_count = APIToken.objects.filter(
            user=self.user
        ).count()

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            content
        )

        self.assertEqual(
            final_api_token_count,
            initial_api_token_count + 1
        )
    
    def test_user_cannot_create_api_token(self):
        # initial_api_token_count = APIToken.objects.filter(
        #     user=self.user
        # ).count()
        
        self.client.force_authenticate(user=self.user)       

        data_post = {
            'purpose': 'New Service',
            'email': self.user.email,
        }

        response = self.client.post(
            reverse('api-token-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            content
        )

    def test_admin_can_list_all_api_tokens(self):
        """ Ensure staff can list all api tokens """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse('api-token-list'),
        )

        content = json.loads(response.content)

        print('$$$$$$$')
        print(content)
        print('$$$$$$$$$$$$')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['count'], 3)
        self.assertEqual(
            content['results'][0]['purpose'],
            'Service alpha')
        self.assertEqual(
            content['results'][1]['purpose'],
            'Service beta')
        self.assertEqual(
            content['results'][2]['purpose'],
            'Service gamma')

    def test_user_cannot_list_api_tokens(self):
        """ Ensure an authenticated user
        cannot list api tokens 
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse('api-token-list'),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(content['detail'], 'You do not have permission to perform this action.')

    def test_unauthenticated_user_cannot_list_any_api_tokens(self):
        """ Ensure an unauthenticated user
        cannot list any api tokens
        """

        response = self.client.get(
            reverse('api-token-list'),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(content['detail'], 'Authentication credentials were not provided.')
