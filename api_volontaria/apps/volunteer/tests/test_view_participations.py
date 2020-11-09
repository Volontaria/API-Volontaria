import json
from datetime import datetime

import os
from pathlib import Path
from decouple import config, Csv
from dj_database_url import parse as db_url

from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse

from django.core import mail
from django.test.utils import override_settings

# from decouple import config
import responses

from api_volontaria.email import EmailAPI
from api_volontaria.apps.log_management.models import EmailLog

from api_volontaria.apps.volunteer.models import (
    Participation,
    Cell,
    TaskType,
    Event,
)
from api_volontaria.factories import (
    UserFactory,
    AdminFactory,
)
from api_volontaria.testClasses import CustomAPITestCase

import pytz
from django.conf import settings
LOCAL_TIMEZONE = pytz.timezone(settings.TIME_ZONE)


class ParticipationsTests(CustomAPITestCase):

    BASE_DIR = Path(__file__).absolute().parent.parent

    ATTRIBUTES = [
        'id',
        'url',
        'event',
        'user',
        'presence_duration_minutes',
        'presence_status',
        'is_standby',
        'registered_at',
    ]

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.user2 = UserFactory()
        self.user2.set_password('Test123!')
        self.user2.save()

        self.user3 = UserFactory()
        self.user3.email = 'yfoucault@innergex.com'
        self.user3.set_password('Test123!')
        self.user3.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

        self.cell = Cell.objects.create(
            name='My new cell',
            address_line_1='373 Rue villeneuve E',
            postal_code='H2T 1M1',
            city='Montreal',
            state_province='Quebec',
            longitude='45.540237',
            latitude='-73.603421',
        )

        self.tasktype = TaskType.objects.create(
            name='My new tasktype',
        )

        self.event = Event.objects.create(
            start_time=LOCAL_TIMEZONE.localize(datetime(2140, 1, 15, 8)),
            end_time=LOCAL_TIMEZONE.localize(datetime(2140, 1, 17, 12)),
            nb_volunteers_needed=10,
            nb_volunteers_standby_needed=0,
            cell=self.cell,
            task_type=self.tasktype,
        )

        self.event2 = Event.objects.create(
            start_time=LOCAL_TIMEZONE.localize(datetime(2140, 1, 15, 8)),
            end_time=LOCAL_TIMEZONE.localize(datetime(2140, 1, 17, 12)),
            nb_volunteers_needed=10,
            nb_volunteers_standby_needed=0,
            cell=self.cell,
            task_type=self.tasktype,
        )

        self.participation = Participation.objects.create(
            event=self.event2,
            user=self.user,
            is_standby=False,
        )

        self.participation2 = Participation.objects.create(
            event=self.event2,
            user=self.user2,
            is_standby=False,
        )

    def test_create_new_participation_as_admin(self):
        """
        Ensure we can create a new participation if we are an admin.
        """
        data_post = {
            'event': reverse(
                'event-detail',
                args=[self.event.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.admin.id],
            ),
            'is_standby': False,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('participation-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            content
        )
        self.check_attributes(content)

    def test_create_new_participation(self):
        """
        Ensure we can create a new participation if we are a simple user.
        """
        data_post = {
            'event': reverse(
                'event-detail',
                args=[self.event.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user.id],
            ),
            'is_standby': False,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('participation-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            content
        )
        self.check_attributes(content)

    def test_create_new_participation_for_an_other_user(self):
        """
        Ensure we can't create a new participation for an other user
        if we are a simple user.
        """
        data_post = {
            'event': reverse(
                'event-detail',
                args=[self.event.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user2.id],
            ),
            'is_standby': False,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('participation-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            content
        )
        self.assertEqual(
            content,
            {
                'user': [
                    "You don't have the right to create a participation "
                    "for an other user"
                ]
            }
        )

    def test_create_new_participation_for_an_other_user_as_admin(self):
        """
        Ensure we can create a new participation for an other user
        if we are an administrator.
        """
        data_post = {
            'event': reverse(
                'event-detail',
                args=[self.event.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user2.id],
            ),
            'is_standby': False,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('participation-list'),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            content
        )
        self.check_attributes(content)

    def test_update_participation_as_admin(self):
        """
        Ensure we can update a participation if we are an admin.
        """
        new_value = True
        data_post = {
            'is_standby': new_value,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'participation-detail',
                kwargs={
                    'pk': self.participation.id
                },
            ),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_attributes(content)
        self.assertEqual(content['is_standby'], new_value)

    def test_update_participation(self):
        """
        Ensure we can't update a participation if we are a simple user.
        """
        new_value = True
        data_post = {
            'is_standby': new_value,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'participation-detail',
                kwargs={
                    'pk': self.participation.id
                },
            ),
            data_post,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            content,
            {
                'detail': 'You do not have permission to perform this action.'
            }
        )

    def test_delete_participation_as_admin(self):
        """
        Ensure we can delete a participation if we are an admin.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'participation-detail',
                kwargs={
                    'pk': self.participation.id
                },
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')

    def test_delete_participation(self):
        """
        Ensure we can't delete a participation if we are a simple user.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'participation-detail',
                kwargs={
                    'pk': self.participation.id
                },
            )
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            content,
            {
                'detail': 'You do not have permission to perform this action.'
            }
        )

    def test_list_participations(self):
        """
        Ensure we can list participations.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse('participation-list'),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content['results']), 1)
        self.check_attributes(content['results'][0])

        for participation in content['results']:
            self.assertEqual(
               participation['user']['id'],
               self.user.id,
            )

    def test_list_participations_as_admin(self):
        """
        Ensure we can list all the participations where we are administrator
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse('participation-list'),
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content['results']), 2)
        self.check_attributes(content['results'][0])

        at_least_one_participation_is_owned_by_somebody_else = False
        for participation in content['results']:
            if participation['user']['id'] != self.admin.id:
                at_least_one_participation_is_owned_by_somebody_else = True

        self.assertTrue(at_least_one_participation_is_owned_by_somebody_else)

    @responses.activate
    @override_settings(
        BASE_DIR = Path(__file__).absolute().parent.parent,
        
        # SECURITY WARNING: keep the secret key used in production secret!
        SECRET_KEY = config('SECRET_KEY'),

        # SECURITY WARNING: don't run with debug turned on in production!
        DEBUG = config('DEBUG', default=False, cast=bool),

        ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=Csv()),


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
        ],

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
        ],

        ROOT_URLCONF = 'api_volontaria.urls',

        SITE_ID = 1,

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
        ],

        WSGI_APPLICATION = 'api_volontaria.wsgi.application',


        # Database
        # https://docs.djangoproject.com/en/2.0/ref/settings/#databases

        DATABASES = {
            'default': config(
                'DATABASE_URL',
                default='sqlite:///' + str(BASE_DIR.joinpath('db.sqlite3')),
                cast=db_url
            )
        },

        # Custom user model

        ACCOUNT_USER_MODEL_USERNAME_FIELD = None,
        ACCOUNT_EMAIL_REQUIRED = True,
        ACCOUNT_EMAIL_VERIFICATION = 'optional',
        ACCOUNT_USERNAME_REQUIRED = False,
        ACCOUNT_AUTHENTICATION_METHOD = 'email',
        AUTH_USER_MODEL = 'user.User',
        ACCOUNT_ADAPTER = 'api_volontaria'\
                        '.apps.user.adapters.AccountAdapter',
        REST_AUTH_SERIALIZERS = {
            'USER_DETAILS_SERIALIZER':
                'api_volontaria'
                '.apps.user.serializers.UserSerializer',
            'PASSWORD_RESET_SERIALIZER':
                'api_volontaria'
                '.apps.user.serializers.CustomPasswordResetSerializer',
        },
        REST_AUTH_REGISTER_SERIALIZERS = {
            'REGISTER_SERIALIZER':
                'api_volontaria'
                '.apps.user.serializers.CustomRegisterSerializer'
        },
        OLD_PASSWORD_FIELD_ENABLED = True,

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
        ],


        # Internationalization
        # https://docs.djangoproject.com/en/2.0/topics/i18n/

        LANGUAGE_CODE = 'en-us',

        TIME_ZONE = 'US/Eastern',

        USE_I18N = True,

        USE_L10N = True,

        USE_TZ = True,


        # Static files (CSS, JavaScript, Images)
        # https://docs.djangoproject.com/en/2.0/howto/static-files/

        STATIC_URL = '/static/',
        STATIC_ROOT = os.path.join(BASE_DIR, 'static/'),

        # Django Rest Framework

        REST_FRAMEWORK = {
            'DEFAULT_RENDERER_CLASSES': (
                'rest_framework.renderers.JSONRenderer',
            ),
            'DEFAULT_AUTHENTICATION_CLASSES': (
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
        },


        # CORS Header Django Rest Framework

        CORS_ORIGIN_ALLOW_ALL = True,


        # Temporary Token

        REST_FRAMEWORK_TEMPORARY_TOKENS = {
            'MINUTES': 10,
            'RENEW_ON_SUCCESS': True,
            'USE_AUTHENTICATION_BACKENDS': False,
        },

        # Activation Token

        ACTIVATION_TOKENS = {
            'MINUTES': 2880,
        },
        ANYMAIL={
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
        },
        EMAIL_BACKEND='anymail.backends.sendinblue.EmailBackend',
        DEFAULT_FROM_EMAIL='noreply@example.org',
        # User specific settings
        LOCAL_SETTINGS={
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
    )
    def test_send_organization_custom_template_confirmation_email(self):
        """
        Ensure an email is sent to participant
        when a participation gets created.
        """

        data_post = {
            'event': reverse(
                'event-detail',
                args=[self.event.id],
            ),
            'user': reverse(
                'user-detail',
                args=[self.user3.id],
            ),
            'is_standby': False,
        }

        print(data_post)
        # print(self.user3.email)  #recipient email ok
        # print(f'user = {data_post["user"]}')

        self.client.force_authenticate(user=self.user3)

        outbox_initial_email_count = len(mail.outbox)

        TEMPLATES = settings.ANYMAIL.get('TEMPLATES')
        id = TEMPLATES.get('CONFIRMATION_PARTICIPATION')

        print(f'id: {id}')  # = 4 ok
        # print(mail.outbox[0])
        # print(mail.outbox[1])

        # print(settings.ANYMAIL['SENDINBLUE_API_KEY'])
        # print(settings.LOCAL_SETTINGS['ORGANIZATION'])

        # print(
        #     email_log.user_email,
        #     email_log.type_email,
        #     email_log.nb_email_sent,
        # )       

        response = self.client.post(
            reverse('participation-list'),
            data_post,
            format='json',
        )

        print(f'response: {response}')

        nb_email_sent = len(mail.outbox) - outbox_initial_email_count

        new_email_log = EmailLog.add(
            user_email=self.user3.user_email,
            type_email=type_email,
            nb_email_sent=nb_email_sent,
            )
        print(new_email_log)

        self.assertEqual(nb_email_sent, 1)

    # @responses.activate
    # @override_settings(
    #     LOCAL_SETTINGS={
    #         'ORGANIZATION': "volontaria",
    #         'CONTACT_EMAIL': config(
    #             'CONTACT_EMAIL'
    #         ),
    #         "EMAIL_SERVICE": False,  # or set to True?
    #         'AUTO_ACTIVATE_USER': False,
    #         'FRONTEND_URLS': {
    #             'BASE_URL': 'http://localhost:4200/',
    #             'RESET_PASSWORD': 'reset-password/{uid}/{token}',
    #         }
    #     },
    #     ANYMAIL={
    #         'SENDINBLUE_API_KEY':
    #         config('SENDINBLUE_API_KEY', default='placeholder_key'),
    #         'REQUESTS_TIMEOUT': (30, 30),
    #         'TEMPLATES': {
    #             'CONFIRMATION_PARTICIPATION': config(
    #                 'TEMPLATE_ID_CONFIRMATION_PARTICIPATION',
    #                 default=0,
    #                 cast=int
    #             ),
    #             'CANCELLATION_PARTICIPATION_EMERGENCY': config(
    #                 'TEMPLATE_ID_CANCELLATION_PARTICIPATION_EMERGENCY',
    #                 default=0,
    #                 cast=int
    #             ),
    #             'RESET_PASSWORD': config(
    #                 'RESET_PASSWORD_EMAIL_TEMPLATE',
    #                 default=0
    #             ),
    #         }
    #     },
    #     # EMAIL_BACKEND='anymail.backends.sendinblue.EmailBackend'
    #     # DEFAULT_FROM_EMAIL='noreply@example.org'
    # )
    # def test_send_default_template_confirmation_email(self):
    #     """
    #     Ensure an email is sent to participant when a participation gets created. 
    #     """

    #     data_post = {
    #         'event': reverse(
    #             'event-detail',
    #             args=[self.event.id],
    #         ),
    #         'user': reverse(
    #             'user-detail',
    #             args=[self.user.id],
    #         ),
    #         'is_standby': False,
    #     }

    #     self.client.force_authenticate(user=self.user)

    #     email_count = len(mail.outbox)

    #     response = self.client.post(
    #         reverse('participation-list'),
    #         data_post,
    #         format='json',
    #     )

    #     TEMPLATES = settings.ANYMAIL.get('TEMPLATES')
    #     id = TEMPLATES.get('CONFIRMATION_PARTICIPATION')

    #     print(mail.outbox[0])

    #     self.assertEqual(len(mail.outbox), email_count + 1)
