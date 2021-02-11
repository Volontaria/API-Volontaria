# import base64

# # import pytest
# from django.conf import settings
# from django.contrib.auth.models import User
# from django.http import HttpResponse
# from django.test import TestCase, override_settings
# from django.urls import include, path

# from rest_framework import (
#     HTTP_HEADER_ENCODING, exceptions, permissions, renderers, status
# )
# # from rest_framework.authentication import (
# #     BaseAuthentication, BasicAuthentication, RemoteUserAuthentication,
# #     SessionAuthentication, TokenAuthentication
# # )
# # from rest_framework.authtoken.models import Token
# from rest_framework.authtoken.views import obtain_auth_token
# from rest_framework.response import Response
# from rest_framework.test import APIClient
# from rest_framework.views import APIView

# # from .models import CustomToken


# from ...models import APIToken

# from api_volontaria.factories import UserFactory, AdminFactory



# # factory = APIRequestFactory()


# # class CustomTokenAuthentication(TokenAuthentication):
# #     model = CustomToken


# # class CustomKeywordTokenAuthentication(TokenAuthentication):
# #     keyword = 'Bearer'


# class MockView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)

#     def get(self, request):
#         return HttpResponse({'a': 1, 'b': 2, 'c': 3})

#     def post(self, request):
#         return HttpResponse({'a': 1, 'b': 2, 'c': 3})

#     def put(self, request):
#         return HttpResponse({'a': 1, 'b': 2, 'c': 3})


# urlpatterns = [
#     path(
#         'token/',
#         MockView.as_view(authentication_classes=[TokenAuthentication])
#     ),
#     path('auth-token/', obtain_auth_token),
#     path('auth/', include('rest_framework.urls', namespace='rest_framework')),
# ]

# class BaseTokenAuthTests:
#     """Token authentication"""
#     model = None
#     path = None
#     header_prefix = 'Token '

#     def setUp(self):
#         # self.csrf_client = APIClient(enforce_csrf_checks=True)
#         # TODO: check that we do not need or want csrf protection

#         self.csrf_client = APIClient(enforce_csrf_checks=True)
        
#         self.user = UserFactory()
#         self.user.save()
#         # TODO: should we test that non-admin user fails to create a token?

#         self.admin = AdminFactory()
#         self.admin.save()


#         # self.username = 'john'
#         # self.email = 'lennon@thebeatles.com'
#         # self.password = 'password'
#         # self.user = User.objects.create_user(
#         #     self.username, self.email, self.password
#         # )

#         self.key = 'abcd1234'
#         self.token = self.model.objects.create(key=self.key, user=self.user)

#     def test_post_form_passing_token_auth(self):
#         """
#         Ensure POSTing json over token auth with correct
#         credentials passes and does not require CSRF
#         """
#         auth = self.header_prefix + self.key
#         response = self.csrf_client.post(
#             self.path, {'example': 'example'}, HTTP_AUTHORIZATION=auth
#         )
#         assert response.status_code == status.HTTP_200_OK
    
#     def test_fail_authentication_if_user_is_not_active(self):
#         user_0 = User.objects.create_user('foo', 'bar', 'baz')
#         user_0.is_active = False
#         user_0.save()
#         self.model.objects.create(key='foobar_token', user=user_0)
#         response = self.csrf_client.post(
#             self.path, {'example': 'example'},
#             HTTP_AUTHORIZATION=self.header_prefix + 'foobar_token'
#         )
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED

#     def test_fail_authentication_if_user_is_not_admin(self):
        
#         self.model.objects.create(key='foobar_token', user=user)
#         response = self.csrf_client.post(
#             self.path, {'example': 'example'},
#             HTTP_AUTHORIZATION=self.header_prefix + 'foobar_token'
#         )
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED

#     def test_fail_post_form_passing_nonexistent_token_auth(self):
#         # use a nonexistent token key
#         auth = self.header_prefix + 'wxyz6789'
#         response = self.csrf_client.post(
#             self.path, {'example': 'example'}, HTTP_AUTHORIZATION=auth
#         )
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED

#     def test_fail_post_if_token_is_missing(self):
#         response = self.csrf_client.post(
#             self.path, {'example': 'example'},
#             HTTP_AUTHORIZATION=self.header_prefix)
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED

#     def test_fail_post_if_token_contains_spaces(self):
#         response = self.csrf_client.post(
#             self.path, {'example': 'example'},
#             HTTP_AUTHORIZATION=self.header_prefix + 'foo bar'
#         )
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED

#     def test_fail_post_form_passing_invalid_token_auth(self):
#         # add an 'invalid' unicode character
#         auth = self.header_prefix + self.key + "¸"
#         response = self.csrf_client.post(
#             self.path, {'example': 'example'}, HTTP_AUTHORIZATION=auth
#         )
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED

#     def test_post_json_passing_token_auth(self):
#         """
#         Ensure POSTing form over token auth with correct
#         credentials passes and does not require CSRF
#         """
#         auth = self.header_prefix + self.key
#         response = self.csrf_client.post(
#             self.path, {'example': 'example'},
#             format='json', HTTP_AUTHORIZATION=auth
#         )
#         assert response.status_code == status.HTTP_200_OK

#     def test_post_json_makes_one_db_query(self):
#         """
#         Ensure that authenticating a user using a
#         token performs only one DB query
#         """
#         auth = self.header_prefix + self.key

#         def func_to_test():
#             return self.csrf_client.post(
#                 self.path, {'example': 'example'},
#                 format='json', HTTP_AUTHORIZATION=auth
#             )

#         self.assertNumQueries(1, func_to_test)

#     def test_post_form_failing_token_auth(self):
#         """
#         Ensure POSTing form over token auth without correct credentials fails
#         """
#         response = self.csrf_client.post(self.path, {'example': 'example'})
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED

#     def test_post_json_failing_token_auth(self):
#         """
#         Ensure POSTing json over token auth without correct credentials fails
#         """
#         response = self.csrf_client.post(
#             self.path, {'example': 'example'}, format='json'
#         )
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED

# @override_settings(ROOT_URLCONF=__name__)
# class TokenAuthTests(BaseTokenAuthTests, TestCase):
#     model = APITokenProxy
#     path = '/token/'

#     def test_token_has_auto_assigned_key_if_none_provided(self):
#         """Ensure creating a token with no key will auto-assign a key"""
#         self.token.delete()
#         # token = self.model.objects.create(user=self.user)
#         token = self.model.objects.create(user=self.admin)
#         assert bool(token.key)

#     def test_generate_key_returns_string(self):
#         """Ensure generate_key returns a string"""
#         token = self.model()
#         key = token.generate_key()
#         assert isinstance(key, str)

#     def test_generate_key_accessible_as_classmethod(self):
#         key = self.model.generate_key()
#         assert isinstance(key, str)

#     def test_token_login_json(self):
#         """Ensure token login view using JSON POST works."""
#         client = APIClient(enforce_csrf_checks=True)
#         response = client.post(
#             '/auth-token/',
#             {'email': self.user.email, 'password': self.user.password},
#             format='json'
#         )
#         assert response.status_code == status.HTTP_200_OK
#         assert response.data['token'] == self.key

#     def test_token_login_json_bad_creds(self):
#         """
#         Ensure token login view using JSON POST fails if
#         bad credentials are used
#         """
#         client = APIClient(enforce_csrf_checks=True)
#         response = client.post(
#             '/auth-token/',
#             {'email': self.user.email, 'password': "badpass"},
#             format='json'
#         )
#         assert response.status_code == 400

#     def test_token_login_json_missing_fields(self):
#         """Ensure token login view using JSON POST fails if missing fields."""
#         client = APIClient(enforce_csrf_checks=True)
#         response = client.post('/auth-token/',
#                                {'email': self.user.email}, format='json')
#         assert response.status_code == 400

#     def test_token_login_form(self):
#         """Ensure token login view using form POST works."""
#         client = APIClient(enforce_csrf_checks=True)
#         response = client.post(
#             '/auth-token/',
#             {'email': self.user.email, 'password': self.password}
#         )
#         assert response.status_code == status.HTTP_200_OK
#         assert response.data['token'] == self.key
