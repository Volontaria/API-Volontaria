import json

from datetime import timedelta

from django.contrib.admin import site

from rest_framework.test import APIClient
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token

from api_volontaria.apps.user.serializers import APITokenSerializer

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
        self.admin = AdminFactory()
        self.user_authtoken = APIToken.objects.create(
            key='test_user_authtoken',
            user=self.user,
            purpose='Because it is hard')
        self.admin_apitoken = APIToken.objects.create(
            key='test_admin_apitoken',
            user=self.admin,
            purpose="Pas dans l'espoir du succès")

    def test_model_admin_displayed_fields(self):
        mock_request = object()
        token_admin = APITokenAdmin(self.admin_apitoken, self.site)
        assert token_admin.get_fields(mock_request) == ('user', 'purpose')

    def test_token_string_representation(self):
        assert str(self.admin_apitoken) == 'test_admin_apitoken'
    
    def test_validate_raise_error_if_no_credentials_provided(self):
        with self.assertRaises(ValidationError):
            APITokenSerializer().validate({})
  
    def test_more_than_one_token_can_be_created_for_single_admin(self):
        token_initial_count = APIToken.objects.filter(
            user=self.admin
        ).count()

        self.token_2 = APIToken.objects.create(
            key='test_admin_apitoken 2',
            user=self.admin, 
            purpose="C'est bien plus beau lorsque c'est inutile",
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
            key='test_admin_apitoken 2',
            user=self.user,
            purpose="Not because it is easy"
        )

        token_final_count = APIToken.objects.filter(
            user=self.user,
        ).count()

        self.assertEqual(token_final_count, token_initial_count + 1)
