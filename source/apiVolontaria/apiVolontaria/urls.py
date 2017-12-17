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
from django.conf.urls import url, include
from django.contrib import admin

from .views import ObtainTemporaryAuthToken, Users, UsersId, UsersActivation

urlpatterns = [
    # Token authentification
    url(
        r'^authentication$',
        ObtainTemporaryAuthToken.as_view(),
        name='token_api'
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
    # Volunteer
    url(
        r'^volunteer/',
        include('volunteer.urls', namespace="volunteer"),
    ),
    # Volunteer
    url(
        r'^location/',
        include('location.urls', namespace="location"),
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
]
