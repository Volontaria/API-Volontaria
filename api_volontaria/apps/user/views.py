from django.contrib.auth import get_user_model, password_validation
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, Permission
from django.utils import timezone
from django.http import Http404
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from rest_framework import status, viewsets, mixins
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import JSONParser
from allauth.socialaccount.providers.facebook.views import (
    FacebookOAuth2Adapter,
)
from rest_auth.registration.views import SocialLoginView

from rest_framework import parsers, renderers
from .models import APIToken
from .serializers import APITokenSerializer
from rest_framework.compat import coreapi, coreschema
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
from rest_framework.schemas import coreapi as coreapi_schema
from rest_framework.views import APIView



from api_volontaria import permissions

# from .models import (
#     ActionToken,
# )

from .models import APIToken

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


class ObtainAPIToken(APIView):
    ''' This class is strongly inspired from ObtainToken in Django Rest Framework
    Some differences are in the post function:
    - the post function has been modified to allow:
        - creating multiple tokens by a single user
        - specifying to which purpose the token relates
    TODO: - a get function has been added to allow user to retrieve:
        - a list of their tokens
        - the token related to a given purpose  
    '''
    
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = APITokenSerializer

    if coreapi_schema.is_enabled():
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="username",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Username",
                        description="Valid username for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        purpose = serializer.validated_data['purpose']
        api_token = APIToken.objects.create(user=user, purpose=purpose)
        return Response({'api_token': api_token.key, 'purpose': api_token.purpose})
    
    def get(self, request, format=None):
        ''' Return to user list of his own API Tokens
        and to admin list of all existing API Tokens 
        '''
        # TypeError: Cannot cast AnonymousUser to int. Are you trying to use it in place of User?
        # requester = self.request.user
        # print('requester: ', requester)
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                api_tokens = APIToken.objects.all()
            else:
                print('----')
                print('mouaf')
                print('----')
                api_tokens = APIToken.objects.filter(user=self.request.user)
            serializer = APITokenSerializer(api_tokens, many=True)
            return Response(serializer.data)
        else:
            print('XXXXX')
            content = {'message': 'Please login or register.'}
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)
        
        # except TypeError as e:
        #     print(f'Error: {e}')
        #     # content = {'message': 'Unauthenticated'}
        #     # return Response(content, status=status.HTTP_401_UNAUTHORIZED)


        # requester = self.request.user
        
        # if requester.is_authenticated():  
        # TODO: fix error above; TypeError: 'bool' object is not callable
            

obtain_api_token = ObtainAPIToken.as_view()
