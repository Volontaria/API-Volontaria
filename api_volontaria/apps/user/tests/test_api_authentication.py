# Standard library
import json
from datetime import datetime
import pytz

# External modules
# from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.conf import settings
# from django.contrib.auth.models import User

# Application modules
from api_volontaria.factories import (
    UserFactory,
)
from api_volontaria.apps.position.models import (
    Position,
    Application,
)
from api_volontaria.testClasses import CustomAPITestCase
from ..models import APIToken


LOCAL_TIMEZONE = pytz.timezone(settings.TIME_ZONE)


class BaseAPITokenAuthTests(CustomAPITestCase):
    """API Token authentication
    This class of tests is strongly inspired from BaseTokenAuthTests
    in django-rest-framework/tests/authentication/test_authentication.py
    """

    path = None  # for DRF-style tests
    header_prefix = 'APIToken '

    def setUp(self):
        # self.csrf_client = APIClient(enforce_csrf_checks=True)
        self.client = APIClient()
        self.user = UserFactory()
        # self.user.set_password('Test123!')
        # self.user.save()
        # self.admin = AdminFactory()
        # self.username = 'john'
        # self.email = 'lennon@thebeatles.com'
        # self.password = 'password'
        # self.user = User.objects.create_user(
        #     self.username, self.email, self.password
        # )

        # print('user: ', self.user)

        self.key = 'abcd1234'
        self.token = APIToken.objects.create(
            key=self.key,
            user=self.user,
            purpose="C'est bien plus beau lorsque c'est inutile",
            )

        self.position = Position.objects.create(
            hourly_wage=14.00,
            weekly_hours=15,
            minimum_days_commitment=3,
            is_remote_job=True,
            is_posted=True,
        )

        # self.application = Application.objects.create(
        #     position=self.position,
        #     user=self.user,
        #     applied_on=LOCAL_TIMEZONE.localize(datetime(2022, 4, 15, 19)),
        #     motivation='passionate about that stuff',
        #     application_status=Application.APPLICATION_ACCEPTED,
        # )

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
        Ensure we cannot create a new application if we are a simple user
        with invalid api token
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


#############################################################################

# TODO: comprendre pourquoi les tests ci-dessous, inspirés de DRF, ne fonctionnent pas

    def test_post_form_passing_token_auth(self):
        """
        Ensure POSTing json over token auth with correct
        credentials passes and does not require CSRF
        """
        auth = self.header_prefix + self.key
        # response = self.csrf_client.post(
        #     self.path, {'example': 'example'}, HTTP_AUTHORIZATION=auth
        # )
        response = self.client.post(
            self.path, {'example': 'example'}, HTTP_AUTHORIZATION=auth
        )
        print('--- response1:')
        print(response)
        print('---')
        assert response.status_code == status.HTTP_200_OK


    # def test_fail_post_form_passing_nonexistent_token_auth(self):
    #     # use a nonexistent token key
    #     auth = self.header_prefix + 'wxyz6789'
    #     response = self.client.post(
    #         self.path, {'example': 'example'}, HTTP_AUTHORIZATION=auth
    #     )
    #     print('--- response2:')
    #     print(response)
    #     print('---')
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # def test_fail_post_if_token_is_missing(self):
    #     response = self.csrf_client.post(
    #         self.path, {'example': 'example'},
    #         HTTP_AUTHORIZATION=self.header_prefix)
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # def test_fail_post_if_token_contains_spaces(self):
    #     response = self.csrf_client.post(
    #         self.path, {'example': 'example'},
    #         HTTP_AUTHORIZATION=self.header_prefix + 'foo bar'
    #     )
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # def test_fail_post_form_passing_invalid_token_auth(self):
    #     # add an 'invalid' unicode character
    #     auth = self.header_prefix + self.key + "¸"
    #     response = self.csrf_client.post(
    #         self.path, {'example': 'example'}, HTTP_AUTHORIZATION=auth
    #     )
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # def test_post_json_passing_token_auth(self):
    #     """
    #     Ensure POSTing form over token auth with correct
    #     credentials passes and does not require CSRF
    #     """
    #     auth = self.header_prefix + self.key
    #     response = self.csrf_client.post(
    #         self.path, {'example': 'example'},
    #         format='json', HTTP_AUTHORIZATION=auth
    #     )
    #     assert response.status_code == status.HTTP_200_OK

    # def test_post_json_makes_one_db_query(self):
    #     """
    #     Ensure that authenticating a user using a
    #     token performs only one DB query
    #     """
    #     auth = self.header_prefix + self.key

    #     def func_to_test():
    #         return self.csrf_client.post(
    #             self.path, {'example': 'example'},
    #             format='json', HTTP_AUTHORIZATION=auth
    #         )

    #     self.assertNumQueries(1, func_to_test)

    # def test_post_form_failing_token_auth(self):
    #     """
    #     Ensure POSTing form over token auth without correct credentials fails
    #     """
    #     response = self.csrf_client.post(self.path, {'example': 'example'})
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # def test_post_json_failing_token_auth(self):
    #     """
    #     Ensure POSTing json over token auth without correct credentials fails
    #     """
    #     response = self.csrf_client.post(
    #         self.path, {'example': 'example'}, format='json'
    #     )
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED
