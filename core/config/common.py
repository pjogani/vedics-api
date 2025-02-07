import os
from distutils.util import strtobool
from os.path import join, dirname, abspath

import dj_database_url
from configurations import Configuration
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from django.utils.translation import gettext_lazy as _  # <-- Added for i18n

BASE_DIR = dirname(dirname(abspath(__file__)))

class Common(Configuration):
    SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'CHANGEME!!!')

    SENTRY_DSN = os.getenv("SENTRY_DSN", "")
    if SENTRY_DSN:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration()],
            traces_sample_rate=0.0,
            send_default_pii=True
        )

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'corsheaders',
        'rest_framework',
        'rest_framework.authtoken',
        'django_filters',
        'drf_spectacular',
        'django.contrib.sites',
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        'allauth.socialaccount.providers.google',
        'core.users',
        'core.conduit',
        'core.organizations',
        'profiles.apps.ProfilesConfig',
        'subscriptions.apps.SubscriptionsConfig',
        'predictions.apps.PredictionsConfig',
        'assistant.apps.AssistantConfig',
        # For storing Celery task results
        'django_celery_results',
    )

    SITE_ID = 1

    MIDDLEWARE = (
        'corsheaders.middleware.CorsMiddleware',
        'core.middleware.UpstreamUserContextMiddleware',
        'core.middleware.LanguageMiddleware',
        'core.middleware.OrganizationAndRoleMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )

    ALLOWED_HOSTS = ["*"]
    ROOT_URLCONF = 'core.urls'
    WSGI_APPLICATION = 'core.wsgi.application'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'corestack',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

    APPEND_SLASH = False
    TIME_ZONE = 'UTC'
    LANGUAGE_CODE = 'en-us'
    # Turn on i18n (previously was False)
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True
    LOGIN_REDIRECT_URL = '/'
    LOGOUT_REDIRECT_URL = '/'

    # Added explicit languages you wish to support
    LANGUAGES = (
        ('en', _('English')),
        ('hi', _('Hindi')),
        ('te', _('Telugu')),
        ('ta', _('Tamil')),
    )

    # Where Django looks for .po/.mo files
    LOCALE_PATHS = [
        os.path.join(BASE_DIR, 'locale'),
    ]

    STATIC_ROOT = os.path.normpath(join(dirname(BASE_DIR), 'static'))
    STATICFILES_DIRS = []
    STATIC_URL = '/static/'
    MEDIA_ROOT = join(dirname(BASE_DIR), 'media')
    MEDIA_URL = '/media/'

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

    DEBUG = strtobool(os.getenv('DJANGO_DEBUG', 'no'))
    AUTH_USER_MODEL = 'users.User'

    REST_FRAMEWORK = {
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 10,
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.TokenAuthentication',
        ),
        'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
        # Added for consistent error responses
        'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
        # Enable URL path versioning
        'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    }

    SPECTACULAR_SETTINGS = {
        'TITLE': 'Corestack API',
        'DESCRIPTION': 'API documentation for the Corestack project.',
        'VERSION': '1.0.0',
        'SERVE_INCLUDE_SCHEMA': False,
    }

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'allauth.account.auth_backends.AuthenticationBackend',
    )

    # django-allauth configuration
    ACCOUNT_EMAIL_REQUIRED = True
    ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    ACCOUNT_AUTHENTICATION_METHOD = "username_email"
    ACCOUNT_LOGOUT_ON_GET = True
    ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
    ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
    ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300

    SOCIALACCOUNT_PROVIDERS = {
        'google': {
            'SCOPE': [
                'profile',
                'email',
            ],
            'AUTH_PARAMS': {
                'access_type': 'online',
            }
        }
    }

    # Celery
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
    CELERY_RESULT_BACKEND = 'django-db'  # Django Celery Results

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
            'django.request': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': False,
            },
        }
    }

    # Default local cache backend (can be overridden in production)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': '',
        }
    }
