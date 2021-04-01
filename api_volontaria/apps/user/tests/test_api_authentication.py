# Standard library
import json
from datetime import datetime

# External modules
# from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

# Application modules
from api_volontaria.factories import (
    UserFactory,
)
from api_volontaria.testClasses import CustomAPITestCase
from ..models import APIToken


class BaseAPITokenAuthTests(CustomAPITestCase):
    """API Token authentication
    This class of tests is strongly inspired from BaseTokenAuthTests
    in django-rest-framework/tests/authentication/test_authentication.py
    """

    model = None
    path = None
    header_prefix = 'Token '

    def setUp(self):
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        self.user = UserFactory()
        # self.admin = AdminFactory()
        # self.username = 'john'
        # self.email = 'lennon@thebeatles.com'
        # self.password = 'password'
        # self.user = User.objects.create_user(
        #     self.username, self.email, self.password
        # )

        self.key = 'abcd1234'
        self.token = APIToken.objects.create(
            key=self.key,
            user=self.user,
            purpose="C'est bien plus beau lorsque c'est inutile",
            )

    def test_post_form_passing_token_auth(self):
        """
        Ensure POSTing json over token auth with correct
        credentials passes and does not require CSRF
        """
        auth = self.header_prefix + self.key
        response = self.csrf_client.post(
            self.path, {'example': 'example'}, HTTP_AUTHORIZATION=auth
        )
        assert response.status_code == status.HTTP_200_OK

    def test_fail_authentication_if_user_is_not_active(self):
        user1 = UserFactory()
        user1.is_active = False
        user1.save()
        APIToken.objects.create(key='foobar_token', user=user1, purpose='Service A')
        response = self.csrf_client.post(
            self.path, {'example': 'example'},
            HTTP_AUTHORIZATION=self.header_prefix + 'foobar_token'
        )
        print('---')
        print('response', response)
        print(response.status_code)
        print('---')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_fail_post_form_passing_nonexistent_token_auth(self):
        # use a nonexistent token key
        auth = self.header_prefix + 'wxyz6789'
        response = self.csrf_client.post(
            self.path, {'example': 'example'}, HTTP_AUTHORIZATION=auth
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_fail_post_if_token_is_missing(self):
        response = self.csrf_client.post(
            self.path, {'example': 'example'},
            HTTP_AUTHORIZATION=self.header_prefix)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_fail_post_if_token_contains_spaces(self):
        response = self.csrf_client.post(
            self.path, {'example': 'example'},
            HTTP_AUTHORIZATION=self.header_prefix + 'foo bar'
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_fail_post_form_passing_invalid_token_auth(self):
        # add an 'invalid' unicode character
        auth = self.header_prefix + self.key + "¸"
        response = self.csrf_client.post(
            self.path, {'example': 'example'}, HTTP_AUTHORIZATION=auth
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_post_json_passing_token_auth(self):
        """
        Ensure POSTing form over token auth with correct
        credentials passes and does not require CSRF
        """
        auth = self.header_prefix + self.key
        response = self.csrf_client.post(
            self.path, {'example': 'example'},
            format='json', HTTP_AUTHORIZATION=auth
        )
        assert response.status_code == status.HTTP_200_OK

    def test_post_json_makes_one_db_query(self):
        """
        Ensure that authenticating a user using a
        token performs only one DB query
        """
        auth = self.header_prefix + self.key

        def func_to_test():
            return self.csrf_client.post(
                self.path, {'example': 'example'},
                format='json', HTTP_AUTHORIZATION=auth
            )

        self.assertNumQueries(1, func_to_test)

    def test_post_form_failing_token_auth(self):
        """
        Ensure POSTing form over token auth without correct credentials fails
        """
        response = self.csrf_client.post(self.path, {'example': 'example'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_post_json_failing_token_auth(self):
        """
        Ensure POSTing json over token auth without correct credentials fails
        """
        response = self.csrf_client.post(
            self.path, {'example': 'example'}, format='json'
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
