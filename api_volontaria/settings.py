"""
Django settings for API-Volontaria project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
from pathlib import Path
from decouple import config, Csv
from dj_database_url import parse as db_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).absolute().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=Csv())


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'allauth',
    'allauth.account',
    'rest_auth.registration',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'corsheaders',
    'api_volontaria',
    'api_volontaria.apps.user',
    'api_volontaria.apps.notification',
    'anymail',
    'import_export',
    'simple_history',
    'dry_rest_permissions',
    'api_volontaria.apps.log_management',
    'api_volontaria.apps.page',
    'api_volontaria.apps.volunteer',
    'api_volontaria.apps.position',
    'django_filters',
    'djmoney',
    'debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'api_volontaria.urls'

SITE_ID = 1

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'api_volontaria.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': config(
        'DATABASE_URL',
        default='sqlite:///' + str(BASE_DIR.joinpath('db.sqlite3')),
        cast=db_url
    )
}

# Custom user model

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
AUTH_USER_MODEL = 'user.User'
ACCOUNT_ADAPTER = 'api_volontaria'\
                  '.apps.user.adapters.AccountAdapter'
REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER':
        'api_volontaria'
        '.apps.user.serializers.UserSerializer',
    'PASSWORD_RESET_SERIALIZER':
        'api_volontaria'
        '.apps.user.serializers.CustomPasswordResetSerializer',
}
REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER':
        'api_volontaria'
        '.apps.user.serializers.CustomRegisterSerializer'
}
OLD_PASSWORD_FIELD_ENABLED = True

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Eastern'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Django Rest Framework

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BaseAuthentication',
        'api_volontaria.apps.user.authentication.APITokenAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter'
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.'
                                'LimitOffsetPagination',
    'PAGE_SIZE': 100
}


# CORS Header Django Rest Framework

CORS_ORIGIN_ALLOW_ALL = True


# Temporary Token

REST_FRAMEWORK_TEMPORARY_TOKENS = {
    'MINUTES': 10,
    'RENEW_ON_SUCCESS': True,
    'USE_AUTHENTICATION_BACKENDS': False,
}

# Activation Token

ACTIVATION_TOKENS = {
    'MINUTES': 2880,
}

ANYMAIL = {
    'SENDINBLUE_API_KEY':
    config('SENDINBLUE_API_KEY', default='placeholder_key'),
    'REQUESTS_TIMEOUT': (30, 30),
    'TEMPLATES': {
        'CONFIRMATION_PARTICIPATION': config(
            'TEMPLATE_ID_CONFIRMATION_PARTICIPATION',
            default=0,
            cast=int
        ),
        'CANCELLATION_PARTICIPATION_EMERGENCY': config(
            'TEMPLATE_ID_CANCELLATION_PARTICIPATION_EMERGENCY',
            default=0,
            cast=int
        ),
        'RESET_PASSWORD': config(
            'RESET_PASSWORD_EMAIL_TEMPLATE',
            default=0
        ),
    }
}

EMAIL_BACKEND = 'anymail.backends.sendinblue.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@example.org'

# User specific settings
LOCAL_SETTINGS = {
    'ORGANIZATION': config(
        'ORGANIZATION',
        default='Volontaria'),
    'CONTACT_EMAIL': config(
            'CONTACT_EMAIL',
            default='noreply@volontaria.org',
    ),
    'EMAIL_SERVICE': config(
        'EMAIL_SERVICE',
        default=False,
    ),
    'AUTO_ACTIVATE_USER': False,
    'FRONTEND_URLS': {
        'BASE_URL': 'http://localhost:4200/',
        'RESET_PASSWORD': 'reset-password/{uid}/{token}',
    },
}

NUMBER_OF_DAYS_BEFORE_EMERGENCY_CANCELLATION = 2

# For debug toolbar, including in Docker
# see William Vincent, Django for Professionals, 3.1, Chapter 15 "Performance"
# Ensure that our INTERNAL_IPS matches that of our Docker host
import socket
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())

INTERNAL_IPS = [
    # ...
    # '127.0.0.1',
    # '0.0.0.0',
    [ip[:-1] + '1' for ip in ips],
    # ...
]


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = './static/'
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATICFILES_DIR = (os.path.join(BASE_DIR, "static"),)

try:
    from api_volontaria.local_settings import *
except ImportError:
    pass
