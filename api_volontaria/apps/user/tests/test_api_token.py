# Standard library
import json
from datetime import timedelta
from os import PRIO_PGRP

# Third-party libraries
from django.contrib.admin import site
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

# Application modules
from api_volontaria.apps.user.serializers import APITokenSerializer
from api_volontaria.factories import UserFactory, AdminFactory
from ....testClasses import CustomAPITestCase
from ..models import APIToken
from ..admin import APITokenAdmin
from api_volontaria.apps.user.views import APITokenViewSet


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

    # Two generic tests strongly inspired 
    # from DRF testing suite for Token

    def test_model_admin_displayed_fields(self):
        mock_request = object()
        token_admin = APITokenAdmin(self.admin_apitoken, self.site)
        assert token_admin.get_fields(mock_request) == ('user', 'purpose')

    def test_token_string_representation(self):
        assert str(self.admin_apitoken) == 'test_admin_apitoken'

    # Tests tailored to Volontaria API Token
    # permission system:
    # Admin has all write and read permissions
    # Users have none
    
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

        response = self.client.post(
            reverse('api-token-list'),
            data_post,
            format='json',
        )

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
            reverse('api-token-list'),
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
            reverse('api-token-list'),
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

    def test_error_on_create_when_email_does_not_match_any_active_user_email(self):
        """ Ensure token cannot be created for inactive user """
        
        self.client.force_authenticate(user=self.admin)       

        data_post = {
            'purpose': 'New Service',
            'user_email': self.user.email + "charabia",
        }

        response = self.client.post(
            reverse('api-token-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            content
        )

        self.assertEqual(
            content.get('detail'),
            'Unable to create an API token: there is no active'
            ' user with the email you provided.'
        )

    def test_admin_can_list_all_api_tokens(self):
        """ Ensure staff can list all api tokens """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse('api-token-list'),
        )

        content = json.loads(response.content)

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

    def test_unauthenticated_user_cannot_list_api_tokens(self):
        """ Ensure an unauthenticated user
        cannot list api tokens
        """

        response = self.client.get(
            reverse('api-token-list'),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(content['detail'], 'Authentication credentials were not provided.')

    def test_filter_api_tokens_on_purpose_field(self):
        """ Ensure api tokens matching selected purpose are listed """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            '/'.join([
                reverse('api-token-list'),
                '?purpose=Service+alpha',
            ]),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['count'], 1)
        self.assertEqual(
            content['results'][0]['purpose'],
            'Service alpha')

    def test_filter_api_tokens_on_purpose_field_with_non_existing_value(self):
        """ Ensure an empty list is returned when no match """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            '/'.join([
                reverse('api-token-list'),
                '?purpose=Service+unknown',
            ]),
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['count'], 0)
        self.assertEqual(content['results'],[])

    def test_filter_api_tokens_on_user_email_field(self):
        """ Ensure api tokens matching selected user_email are listed """

        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            ''.join([
                reverse('api-token-list'),
                '/',
                '?user_email=',
                self.admin.email,
            ]),
            format='json'
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['count'], 1)
        self.assertEqual(
            content['results'][0]['user_email'],
            self.admin.email)
        self.assertEqual(
            content['results'][0]['purpose'],
            'Service gamma')

    def test_filter_api_tokens_on_user_email_field_with_non_existing_value(self):
        """ Ensure an empty list is returned when no match """

        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            '/'.join([
                reverse('api-token-list'),
                '?user_email=yenapas',
            ]),
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['count'], 0)
        self.assertEqual(content['results'],[])

    def test_filter_api_tokens_on_both_user_email_and_purpose_fields(self):
        """
        Ensure api tokens matching both selected user_email 
        and selected purpose are listed
        """

        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            ''.join([
                reverse('api-token-list'),
                '/',
                '?purpose=Service alpha',
                '&',
                '?user_email=',
                self.user.email,
            ]),
            format='json'
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['count'], 1)
        self.assertEqual(
            content['results'][0]['user_email'],
            self.user.email)
        self.assertEqual(
            content['results'][0]['purpose'],
            'Service alpha')
