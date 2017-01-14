""" Static settings for supervisr and supervisr.* """

import logging
import os
import sys

from django.contrib import messages

LOGGER = logging.getLogger(__name__)

CRISPY_TEMPLATE_PACK = 'bootstrap3'
NOCAPTCHA = True

SYSLOG_HOST = '127.0.0.1'
SYSLOG_PORT = 514
EMAIL_HOST = 'prd-mail01.prs.fr.beryju.org'
EMAIL_FROM = 'BeryJu.org Beta <my@beryju.org>'
# WARNING!
# This can only be changed before the first `migrate` is run
# If you change this afterwards, it may cause serious damage!
SYSTEM_USER_NAME = 'System'
USER_PROFILE_ID_START = 5000

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'

CHANGELOG = '' # This gets overwritten with ../../CHANGELOG.md on launch
VERSION_HASH = None # This gets overwritten with the current commit's hash on launch
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/static"
SECRET_KEY = '--a*212*x(2z-#muz3(lai@l&f23da6-()m2z4^$up6_y=1%fg'
DEBUG = True
ALLOWED_HOSTS = ['*']
REMEMBER_SESSION_AGE = 60 * 60 * 24 * 30 # One Month

# Settings are taken from DB, these are needed for django-recaptcha to work
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''

LDAP_ENABLED = False
LDAP = {
    'SERVERS': '',
    'BASE': '',
    'CREATE_BASE': '',
    'BIND_USER': '',
    'BIND_PASS': '',
    'DOMAIN': '',
    'PORT': 389,
}

INSTALLED_APPS = [
    'jet.dashboard',
    'jet',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'captcha',
    'supervisr',
    'supervisr_dns',
    'supervisr_server',
    'supervisr_web',
    'supervisr_mail',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'supervisr.middleware.MaintenanceMode.maintenance_mode'
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

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '_dev.db',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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

sys.path.append('..')
try:
    # pylint: disable=wildcard-import
    from local_settings import *
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
