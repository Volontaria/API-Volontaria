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
from django.conf.urls.static import static
from django.contrib import admin

from .views import (ObtainTemporaryAuthToken, Users, UsersId, UsersActivation,
                    ResetPassword, ChangePassword)

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
    # Faq
    url(
        r'^faqs/',
        include('faq.urls', namespace="faq"),
    ),
    # DOCUMENTATION SWAGGER
    url(
        r'^documentation/',
        include('rest_framework_docs.urls')
    ),
    # Admin panel
    url(
        r'^admin/',
        admin.site.urls
    ),

    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^filebrowser_filer/', include('ckeditor_filebrowser_filer.urls')),
]

if settings.DEBUG:
    urlpatterns += [
      # ... the rest of your URLconf goes here ...
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
