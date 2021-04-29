"""The `urlpatterns` list routes URLs to views.
For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls import include, url
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import (DefaultRouter) #, SimpleRouter,
#     Route, DynamicRoute)

# External application routers
# ie: from app.urls import router as app_router
from api_volontaria.apps.user.views import FacebookLogin

from . import views

# from api_volontaria.apps.user.views import obtain_api_token


class OptionalSlashDefaultRouter(DefaultRouter):
    """ Subclass of DefaultRouter to make the trailing slash optional """

    def __init__(self, *args, **kwargs):
        super(DefaultRouter, self).__init__(*args, **kwargs)
        self.trailing_slash = '/?'


# class CustomReadOnlyRouter(SimpleRouter):
#     """
#     A router for read-only APIs, which doesn't use trailing slashes.
#     Stronlgy inspired from DRF API Guide
#     """
#     routes = [
#         Route(
#             url=r'^{prefix}$',
#             mapping={'get': 'list'},
#             name='{basename}-list',
#             detail=False,
#             initkwargs={'suffix': 'List'}
#         ),
#         Route(
#             url=r'^{prefix}/{lookup}$',
#             mapping={'get': 'retrieve'},
#             name='{basename}-detail',
#             detail=True,
#             initkwargs={'suffix': 'Detail'}
#         )
        # DynamicRoute(
        #     url=r'^{prefix}/{lookup}/{url_path}$',
        #     name='{basename}-{url_name}',
        #     detail=True,
        #     initkwargs={}
        # )
    # ]


# Create one or more routers and register our viewsets with them.
router = OptionalSlashDefaultRouter()
# read_only_router = CustomReadOnlyRouter()

# External workplace application
# ie: router.registry.extend(app_router.registry)

# Main application routes
router.register('users', views.UserViewSet)
router.register('single-api-token', views.SingleAPITokenViewSet, basename='single-api-token')
router.register('api-tokens', views.MultipleAPITokenViewSet, basename='api-token')
# router.register('api-tokens', views.APITokenView, basename='api-token')

# read_only_router.register(
#     'api-token-inventories', 
#     views.APITokenReadOnlyViewSet, 
#     basename='api-token-inventory'
# )

urlpatterns = [
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^accounts/', include('allauth.urls'), name='socialaccount_signup'),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^rest-auth/facebook/$', FacebookLogin.as_view(), name='fb_login'),
    path('', include(router.urls)),  # includes router generated URL
    # path('', include(read_only_router.urls)),
    # url(r'^api-token-creation/', obtain_api_token, name='api_token_creation'),
]
