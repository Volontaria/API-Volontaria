# Standard library
import json
from datetime import datetime
import pytz

# Third-party libraries
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.conf import settings
from django.test import TestCase

# Application modules
from api_volontaria.factories import (
    AdminFactory,
    UserFactory,
)
from api_volontaria.apps.position.models import (
    Position,
    Application,
)
from api_volontaria.testClasses import CustomAPITestCase
from ..models import APIToken


LOCAL_TIMEZONE = pytz.timezone(settings.TIME_ZONE)


class APITokenAuthTests(CustomAPITestCase):
    """ Testing API token usage as credential
    when trying to perform legitimate actions
    in Volontaria settings
    """

    header_prefix = 'APIToken '

    def setUp(self):
        self.client = APIClient()
        self.admin = AdminFactory()
        self.user = UserFactory()
        self.user1 = UserFactory()
    
        self.key = 'abcd1234'
        self.token = APIToken.objects.create(
            key=self.key,
            user=self.user,
            purpose="C'est bien plus beau lorsque c'est inutile",
            )

        self.key1 = 'efgh5678'
        self.token1 = APIToken.objects.create(
            key=self.key1,
            user=self.user,
            purpose="Service alpha",
            )

        self.position = Position.objects.create(
            hourly_wage=14.00,
            weekly_hours=15,
            minimum_days_commitment=3,
            is_remote_job=True,
            is_posted=True,
        )

    def test_create_new_application_when_passing_api_token(self):
        """
        Ensure we can create a new application if we are a simple user
        authentified with an API Token
        """
        data_post = {
            'position': reverse(
                'position-detail',
                args=[self.position.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user.id],
            ),
            'motivation': 'seems fun',
        }

        auth = self.header_prefix + self.key

        response = self.client.post(
            reverse('application-list'),
            data_post,
            format='json',
            HTTP_AUTHORIZATION=auth,
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            content
        )

    def test_fail_create_new_application_when_passing_invalid_api_token(self):
        """
        Ensure we cannot create a new application
        if we are a simple user with invalid api token
        """
        data_post = {
            'position': reverse(
                'position-detail',
                args=[self.position.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user.id],
            ),
            'motivation': 'seems fun',
        }

        auth = self.header_prefix + 'charabia'

        response = self.client.post(
            reverse('application-list'),
            data_post,
            format='json',
            HTTP_AUTHORIZATION=auth,
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertEqual(
            content['detail'],
            'Invalid token.'
        )


class BaseTokenAuthTests:
    """
    Token authentication
    Strongly inspired from
    tests/authentication/test_authentication.py
    (which cannot be imported from rest_framewok
    as such (being outside rest_framework),
    so copied-pasted below,
    with some adjustments made as needed 
    to fit Volontaria application)
    """
    model = None
    path = None
    header_prefix = None

    def setUp(self):
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        self.user = UserFactory()

        self.key = 'abcd1234'
        self.token = self.model.objects.create(
            key=self.key, 
            user=self.user, 
            purpose="Helpful service")
        
        self.position = Position.objects.create(
            hourly_wage=14.00,
            weekly_hours=15,
            minimum_days_commitment=3,
            is_remote_job=True,
            is_posted=True,
        )

        self.application = Application.objects.create(
            position=self.position,
            user=self.user,
            applied_on=LOCAL_TIMEZONE.localize(datetime(2022, 4, 15, 19)),
            motivation='passionate about that stuff',
            application_status=Application.APPLICATION_ACCEPTED,
        )

    def test_post_form_passing_token_auth(self):
        """
        Ensure POSTing json over token auth with correct
        credentials passes and does not require CSRF
        """
        auth = self.header_prefix + self.key

        data_post = {
            'position': reverse(
                'position-detail',
                args=[self.position.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user.id],
            ),
            'motivation': self.application.motivation,
        }

        response = self.csrf_client.post(
            reverse('application-list'),
            data_post,
            HTTP_AUTHORIZATION=auth,
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            content
        )

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
        Ensure POSTing json over token auth with correct
        credentials passes and does not require CSRF
        """
        auth = self.header_prefix + self.key

        data_post = {
            'position': reverse(
                'position-detail',
                args=[self.position.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user.id],
            ),
            'motivation': self.application.motivation,
        }

        response = self.csrf_client.post(
            reverse('application-list'),
            data_post,
            format = 'json',
            HTTP_AUTHORIZATION=auth,
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            content
        )

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


class CustomAPITokenAuthTests(BaseTokenAuthTests, TestCase):
    """ This class of tests is stronlgy inspired
    from CustomKeywordTokenAuthTests class in
    django-rest-framework
    /tests/authentication/test_authentication.py
    """

    model = APIToken
    path = '/applications/'
    header_prefix = 'APIToken '
