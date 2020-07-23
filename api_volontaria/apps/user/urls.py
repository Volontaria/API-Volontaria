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
from rest_framework.routers import DefaultRouter
from api_volontaria.apps.user.views import FacebookLogin

# External application routers
# ie: from app.urls import router as app_router

from . import views


class OptionalSlashDefaultRouter(DefaultRouter):
    """ Subclass of DefaultRouter to make the trailing slash optional """

    def __init__(self, *args, **kwargs):
        super(DefaultRouter, self).__init__(*args, **kwargs)
        self.trailing_slash = '/?'


# Create a router and register our viewsets with it.
router = OptionalSlashDefaultRouter()

# External workplace application
# ie: router.registry.extend(app_router.registry)

# Main application routes
router.register('users', views.UserViewSet)

urlpatterns = [
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^accounts/', include('allauth.urls'), name='socialaccount_signup'),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^rest-auth/facebook/$', FacebookLogin.as_view(), name='fb_login'),
    path('', include(router.urls)),  # includes router generated URL
]
