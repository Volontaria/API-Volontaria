import os
from django.utils.translation import ugettext_lazy as _
from builtins import ImportError

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_docs',
    'rest_framework.authtoken',
    'corsheaders',
    'import_export',
    'anymail',
    'storages',
    'orderable',
    'ckeditor',
    'reversion',

    'apiVolontaria',
    'volunteer',
    'location',
    'coupons',
    'pages',

]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
WSGI_APPLICATION = 'apiVolontaria.wsgi.application'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR + '/apiVolontaria/templates/',
        ],
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

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.'
                'auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.'
                'auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.'
                'auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.'
                'password_validation.NumericPasswordValidator',
    },
]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'm_u0yee1g84_g9l89ip@vkw2(03c8ax6esl-6%d471oe5%17-_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*', ]

ROOT_URLCONF = 'apiVolontaria.urls'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Canada/Eastern'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Local path
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(os.path.dirname(PROJECT_DIR), 'static')
# STATICFILES_DIRS = (
#         os.path.join(PROJECT_DIR, 'static'),
#     )
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
#
# MEDIA_ROOT = os.path.join(BASE_DIR, 'project/media')
# MEDIA_URL = 'media/'
# DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media')

CONSTANT = {
    'ORGANIZATION': 'NousRire',
    "EMAIL_SERVICE": True,
    "AUTO_ACTIVATE_USER": False,
    "FRONTEND_INTEGRATION": {
        "ACTIVATION_URL": "127.0.0.1:8000/register/activation/{{token}}",
        "FORGOT_PASSWORD_URL": "127.0.0.1:8000/forgot_password/{{token}}",
    },
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apiVolontaria.authentication.TemporaryTokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.'
                                'LimitOffsetPagination',
    'PAGE_SIZE': 100
}

# CORS Header Django Rest Framework

CORS_ORIGIN_ALLOW_ALL = True

REST_FRAMEWORK_TEMPORARY_TOKENS = {
    'MINUTES': 1000,
    'RENEW_ON_SUCCESS': True,
    'USE_AUTHENTICATION_BACKENDS': False,
}

# Activation Token

ACTIVATION_TOKENS = {
    'MINUTES': 2880,
}

# Email service configuration (using Anymail).
# Refer to Anymail's documentation for configuration details.
ANYMAIL = {
    "SENDINBLUE_API_KEY": "SENDINBLUE_API_KEY",
    'TEMPLATES': {
        'CONFIRM_SIGN_UP': 'example_template_id',
        'FORGOT_PASSWORD': 'example_template_id',
        'COUPON': 'example_template_id',
        'CONFIRM_PARTICIPATION': 'example_template_id',  # Todo
        'CALENDAR_INVITATION': 'example_template_id',  # Todo
    },
}

EMAIL_BACKEND = 'anymail.backends.sendinblue.EmailBackend'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp-relay.sendinblue.com'
EMAIL_HOST_USER = 'SENDINBLUE_EMAIL'
EMAIL_HOST_PASSWORD = 'SENDINBLUE_PASSWORD'
EMAIL_PORT = 587

WOOCOMERCE_API = {
    'key': 'KEY',
    'secret': 'SECRET',
}

COUPON_SEND_EMAIL = False
CUSTOM_EMAIL = False
DEFAULT_FROM_EMAIL = 'noreply@example.org'

# CKEditor
CKEDITOR_CONFIGS = {
    'default': {
        'width': 855,
        'height': 800,
        'toolbar': [
            ['Format'],
            ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', '-', 'Indent', 'Outdent', '-', 'Table'],
            ['HorizontalRule'],
            ['Link', 'Unlink', 'Anchor'],
            ['-', 'SpecialChar'],
            ['Find', 'Replace'],
            ['Undo', 'Redo'],
            ['Source'],
        ],
    },
}
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_UPLOAD_PATH = 'media/ckeditor-uploads'

try:
    from apiVolontaria.local_settings import *
except ImportError:
    pass
