# Third-party libraries
from django.contrib.auth import get_user_model#, password_validation
from django.conf import settings
# from django.contrib.auth.models import AnonymousUser, Permission
# from django.db.models import Q
# from django.utils import timezone
from django.http import Http404
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db.models.query import QuerySet

from rest_framework import mixins, status, viewsets
# from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.compat import coreapi, coreschema
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
from rest_framework.schemas import coreapi as coreapi_schema

from allauth.socialaccount.providers.facebook.views import (
    FacebookOAuth2Adapter,
)
from rest_auth.registration.views import SocialLoginView

from dry_rest_permissions.generics import DRYPermissions

# Volontaria modules
from .models import APIToken
from .serializers import APITokenSerializer
from api_volontaria import permissions
from . import serializers

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    retrieve:
    Return the given user.

    list:
    Return a list of all existing users.

    create:
    Create a new user instance.

    update:
    Update fields of a user instance.

    delete:
    Sets the user inactive.
    """
    queryset = User.objects.all()
    filter_fields = '__all__'

    def get_serializer_class(self):
        if (self.action == 'update') | (self.action == 'partial_update'):
            return serializers.UserUpdateSerializer
        return serializers.UserSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.all()
        if self.kwargs.get("pk", "") == "me":
            self.kwargs['pk'] = user.id
        return queryset

    def get_permissions(self):
        """
        Returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = []
        elif self.action == 'list':
            permission_classes = [IsAdminUser, ]
        else:
            permission_classes = [
                IsAuthenticated,
                permissions.IsOwner
            ]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().retrieve(request, *args, **kwargs)
        try:
            return super().retrieve(request, *args, **kwargs)
        except Http404:
            raise PermissionDenied

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.is_active = False
            instance.save()
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class APITokenViewSet(viewsets.GenericViewSet,
                        mixins.CreateModelMixin,
                        mixins.ListModelMixin):

    ''' This class is strongly inspired from ObtainAuthToken
    in Django Rest Framework
    Some differences are in the post function:
    - the post function has been modified to allow:
        - creating multiple tokens by a single user
        - specifying to which purpose the token relates
    - the addition of a list function allowing admin to retrieve:
        - a list of all API tokens
        - a list of API tokens filtered
         on the fields 'purpose' and/or 'user_email'  
    '''

    serializer_class = APITokenSerializer
    permission_classes = (DRYPermissions,)
    # queryset = APIToken.objects.all()
    
    #TODO: review this coreapi schema
    # if coreapi_schema.is_enabled():
    #     schema = ManualSchema(
    #         fields=[
    #             coreapi.Field(
    #                 name="email",
    #                 required=True,
    #                 location='form',
    #                 schema=coreschema.String(
    #                     title="Email",
    #                     description="Valid email associated with an active user",
    #                 ),
    #             ),
    #             coreapi.Field(
    #                 name="purpose",
    #                 required=True,
    #                 location='form',
    #                 schema=coreschema.String(
    #                     title="Purpose",
    #                     description="Service to be associated with the API Token",
    #                 ),
    #             ),
    #         ],
    #         encoding="application/json",
    #     )

    def get_queryset(self):
        '''
        Defines a queryset allowing
        for filtering on 'purpose' and/or 'user_email'
        '''
        queryset = APIToken.objects.all()
        selected_purpose = self.request.query_params.get('purpose', None)
        selected_email = self.request.query_params.get('user_email', None)
        if (selected_purpose is not None and selected_email is not None):
            selected_user = User.objects.get(email=selected_email)
            queryset = queryset.filter(
                purpose=selected_purpose
                ).filter(
                user=selected_user
                )
        elif (selected_purpose is not None and selected_email is None):
            queryset = queryset.filter(
                purpose=selected_purpose
                )
        elif (selected_purpose is None and selected_email is not None):
            try:
                selected_user = User.objects.get(email=selected_email)
                queryset = queryset.filter(
                user=selected_user
                )
            except User.DoesNotExist:
                queryset = []
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        purpose = serializer.validated_data['purpose']
        user_email = serializer.validated_data['user_email']
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            content = {
                'detail': 'Unable to create an API token: there is no active user'
                ' with the email you provided.'
                }
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        api_token = APIToken.objects.create(user=user, purpose=purpose)
        return Response(
            {'api_token': api_token.key,
            'purpose': api_token.purpose,
            'email': api_token.user.email},
            status=status.HTTP_201_CREATED
            )

    def list(self, request, *args, **kwargs):
        ''' Get full or partial list of API Tokens,
        as a function of filter criteria
        that are passed by the queryset
        '''

        queryset = self.filter_queryset(self.get_queryset())

        data = [
            {
            'user_email': q.user.email,
            'purpose': q.purpose,
            }
            for q in queryset
        ]

        page = self.paginate_queryset(data)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
