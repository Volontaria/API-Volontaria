"""apiVolontaria URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve

from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls

from ckeditor_api.urls import ckeditor_router
from .views import (ObtainTemporaryAuthToken, Users, UsersId, UsersActivation,
                    ResetPassword, ChangePassword)


class OptionalSlashDefaultRouter(DefaultRouter):
    """ Subclass of DefaultRouter to make the trailing slash optional """
    def __init__(self, *args, **kwargs):
        super(DefaultRouter, self).__init__(*args, **kwargs)
        self.trailing_slash = '/?'


# Create a router and register our viewsets with it.
router = OptionalSlashDefaultRouter()

# External workplace application
# Their urls are directly appended to the main router
# The retreat app is not included here because we needed a url prefix, thus
#   it is included separately at the bottom of this file.
router.registry.extend(ckeditor_router.registry)

urlpatterns = [
    # Token authentification
    url(
        r'^authentication$',
        ObtainTemporaryAuthToken.as_view(),
        name='token_api'
    ),
    # Forgot password
    url(
        r'^reset_password$',
        ResetPassword.as_view(),
        name='reset_password'
    ),
    url(
        r'^change_password$',
        ChangePassword.as_view(),
        name='change_password'
    ),
    # Users
    url(
        r'^users$',
        Users.as_view(),
        name='users'
    ),
    url(
        r'^users/activate$',
        UsersActivation.as_view(),
        name='users_activation',
    ),
    url(
        r'^users/(?P<pk>\d+)$',
        UsersId.as_view(),
        name='users_id',
    ),
    url(
        r'^profile$',
        UsersId.as_view(),
        kwargs=dict(
            profile=True,
        ),
        name='profile',
    ),
    # Volunteer
    url(
        r'^volunteer/',
        include('volunteer.urls', namespace="volunteer"),
    ),
    # Location
    url(
        r'^location/',
        include('location.urls', namespace="location"),
    ),
    # Pages
    url(
        r'^pages/',
        include('pages.urls', namespace="pages"),
    ),
    path(
        '',
        include(router.urls)
    ),  # includes router generated URL
    # DOCUMENTATION SWAGGER
    path(
        'docs/',
        include_docs_urls(
            title=settings.CONSTANT['ORGANIZATION'] + " API",
            authentication_classes=[],
            permission_classes=[]
        )
    ),
    # Admin panel
    url(
        r'^admin/',
        admin.site.urls
    ),
]

if settings.DEBUG:
    urlpatterns = [
        url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL, serve, {
            'document_root': settings.MEDIA_ROOT, 'show_indexes': True
        }),
    ] + urlpatterns
    urlpatterns += staticfiles_urlpatterns()
