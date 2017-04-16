""" Static settings for supervisr and supervisr.* """
####################################################################################################
####################################################################################################
###
### You should not edit this file. These settings are the defaults. To Override Values, copy them
### to ../local_settings.py and modify them there.
###
####################################################################################################
####################################################################################################


































import importlib
import logging
import os
import sys

from django.contrib import messages

SYSLOG_HOST = '127.0.0.1'
SYSLOG_PORT = 514

# WARNING!
# This can only be changed before the first `migrate` is run
# If you change this afterwards, it may cause serious damage!
SYSTEM_USER_NAME = 'System'
USER_PROFILE_ID_START = 5000

REMEMBER_SESSION_AGE = 60 * 60 * 24 * 30 # One Month

LOGGER = logging.getLogger(__name__)

CRISPY_TEMPLATE_PACK = 'bootstrap3'
NOCAPTCHA = True

OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth2_provider.Application'

CORS_ORIGIN_ALLOW_ALL = True
REQUEST_APPROVAL_PROMPT = 'auto'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'captcha',
    'supervisr.apps.SupervisrCoreConfig',
    'supervisr_puppet.apps.SupervisrPuppetConfig',
    'supervisr_dns.apps.SupervisrDNSConfig',
    'supervisr_server.apps.SupervisrServerConfig',
    'supervisr_web.apps.SupervisrWebConfig',
    'supervisr_mail.apps.SupervisrMailConfig',
    'supervisr_mod_2fa.apps.SupervisrMod2FaConfig',
    'supervisr_mod_ldap.apps.SupervisrModLDAPConfig',
    'formtools',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'oauth2_provider',
    'corsheaders',
]

CHANGELOG = '' # This gets overwritten with ../../CHANGELOG.md on launch
VERSION_HASH = None # This gets overwritten with the current commit's hash on launch
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/static"
SECRET_KEY = '_k*@6h2u2@q-dku57hhgzb7tnx*ba9wodcb^s9g0j59@=y(@_o' # noqa Debug SECRET_KEY
DEBUG = True
ALLOWED_HOSTS = ['*']

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'

# Settings are taken from DB, these are needed for django-recaptcha to work
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''

INTERNAL_IPS = ['127.0.0.1']

AUTHENTICATION_BACKENDS = [
    'oauth2_provider.backends.OAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'supervisr.middleware.MaintenanceMode.maintenance_mode',
    'supervisr.middleware.PermanentMessage.permanent_message',
]

# Message Tag fix for bootstrap CSS Classes
MESSAGE_TAGS = {
    messages.DEBUG: 'primary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

ROOT_URLCONF = 'supervisr.urls'

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

WSGI_APPLICATION = 'supervisr.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '_dev.db',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

EMAIL_FROM = 'Supervisr <supervisr@localhost>'

sys.path.append('..')
try:
    # pylint: disable=wildcard-import
    from local_settings import * # noqa
except ImportError as exception:
    LOGGER.warning("Failed to import local_settings because %s", exception)

SERVER_EMAIL = EMAIL_FROM

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': ('[%(asctime)s] %(levelname)s '
                       '[%(name)s::%(funcName)s::%(lineno)s] %(message)s'),
        },
        'syslog': {
            'format': '%(asctime)s supervisr %(funcName)s: %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'syslog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'syslog',
            'address': (SYSLOG_HOST, SYSLOG_PORT)
        }
    },
    'loggers': {
        'supervisr': {
            'handlers': ['console', 'syslog'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['console', 'syslog'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

TEST = False
if 'test' in sys.argv:
    LOGGING = None
    TEST = True

if DEBUG is True:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

# Load subapps's INSTALLED_APPS
for app in INSTALLED_APPS:
    if app.startswith('supervisr') and \
        app != 'supervisr' and \
        not app.startswith('supervisr.'):
        app_package = app.split('.')[0]
        try:
            app_settings = importlib.import_module("%s.settings" % app_package)
            INSTALLED_APPS.extend(getattr(app_settings, 'INSTALLED_APPS', []))
            MIDDLEWARE.extend(getattr(app_settings, 'MIDDLEWARE', []))
        except ImportError:
            pass
