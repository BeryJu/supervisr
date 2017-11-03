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

import raven
from django.contrib import messages

# WARNING!
# This can only be changed before the first `migrate` is run
# If you change this afterwards, it may cause serious damage!
SYSTEM_USER_NAME = 'supervisr'
USER_PROFILE_ID_START = 5000

REMEMBER_SESSION_AGE = 60 * 60 * 24 * 30 # One Month

LOGGER = logging.getLogger(__name__)

NOCAPTCHA = True

CORS_ORIGIN_ALLOW_ALL = True
REQUEST_APPROVAL_PROMPT = 'auto'

CHERRYPY_SERVER = {
    'socket_host': '0.0.0.0',
    'socket_port': 8000,
    'thread_pool': 30
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'captcha',
    'supervisr.core.apps.SupervisrCoreConfig',
    'supervisr.puppet.apps.SupervisrPuppetConfig',
    'supervisr.dns.apps.SupervisrDNSConfig',
    'supervisr.server.apps.SupervisrServerConfig',
    'supervisr.web.apps.SupervisrWebConfig',
    'supervisr.mail.apps.SupervisrMailConfig',
    'supervisr.static.apps.SupervisrStaticConfig',
    'supervisr.mod.auth.ldap.apps.SupervisrModAuthLDAPConfig',
    'supervisr.mod.auth.saml.idp.apps.SupervisrModAuthSAMLProvider',
    'supervisr.mod.auth.oauth.provider.apps.SupervisrModAuthOAuthProviderConfig',
    'supervisr.mod.auth.oauth.client.apps.SupervisrModAuthOAuthClientConfig',
    'supervisr.mod.tfa.apps.SupervisrModTFAConfig',
    'supervisr.mod.stats.graphite.apps.SupervisrModStatGraphiteConfig',
    'supervisr.mod.provider.google.apps.SupervisrModProviderGoogleConfig',
    'supervisr.mod.provider.onlinenet.apps.SupervisrModProviderOnlineNetConfig',
    'formtools',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'raven.contrib.django.raven_compat',
]

VERSION_HASH = raven.fetch_git_sha(os.path.dirname(os.pardir))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))+"/static"
MEDIA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/media"
SECRET_KEY = '_k*@6h2u2@q-dku57hhgzb7tnx*ba9wodcb^s9g0j59@=y(@_o' # noqa Debug SECRET_KEY
DEBUG = True
ALLOWED_HOSTS = ['*']

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
LOGIN_REDIRECT_URL = 'user-index'
LOGIN_URL = 'account-login'

# Settings are taken from DB, these are needed for django-recaptcha to work
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''

INTERNAL_IPS = ['127.0.0.1']

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache'),
        'TIMEOUT': 60,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
    'supervisr.core.middleware.ImpersonateMiddleware.impersonate',
    'supervisr.core.middleware.MaintenanceMode.maintenance_mode',
    'supervisr.core.middleware.PermanentMessage.permanent_message',
]

# Message Tag fix for bootstrap CSS Classes
MESSAGE_TAGS = {
    messages.DEBUG: 'primary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

ROOT_URLCONF = 'supervisr.core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            '.'
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

WSGI_APPLICATION = 'supervisr.core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '_dev.db',
    }
}

DATABASE_ROUTERS = []

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

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

EMAIL_FROM = 'Supervisr <supervisr@localhost>'

LOG_LEVEL_FILE = 'DEBUG'
LOG_LEVEL_CONSOLE = 'DEBUG'
LOG_FILE = '/dev/null'

LOG_SYSLOG_HOST = '127.0.0.1'
LOG_SYSLOG_PORT = 514

SENTRY_DSN = ''

sys.path.append('/etc/supervisr')

def load_local_settings(mod):
    """
    Load module *mod* and apply contents to ourselves
    """
    try:
        loaded_module = importlib.import_module(mod, package=None)
        for key, val in loaded_module.__dict__.items():
            if not key.startswith('__') and not key.endswith('__'):
                globals()[key] = val
        LOGGER.warning("Loaded '%s' as local_settings", mod)
        return True
    except ImportError as exception:
        LOGGER.info('Not loaded %s because %s', mod, exception)
        return False

for modu in [os.environ.get('SUPERVISR_LOCAL_SETTINGS', 'supervisr.local_settings'), 'config']:
    if load_local_settings(modu):
        break

SERVER_EMAIL = EMAIL_FROM

RAVEN_CONFIG = {
    'dsn': SENTRY_DSN,
    'release': VERSION_HASH,
    'environment': 'production' if DEBUG is False else 'development',
    'tags': {'external_domain': ''}
}

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
            'level': LOG_LEVEL_CONSOLE,
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'syslog': {
            'level': LOG_LEVEL_FILE,
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'syslog',
            'address': (LOG_SYSLOG_HOST, LOG_SYSLOG_PORT)
        },
        'file': {
            'level': LOG_LEVEL_FILE,
            'class': 'logging.FileHandler',
            'filename': LOG_FILE,
        },
    },
    'loggers': {
        'supervisr': {
            'handlers': ['console', 'syslog', 'file', 'sentry'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['console', 'syslog', 'file', 'sentry'],
            'level': 'INFO',
            'propagate': True,
        },
        'tasks': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'cherrypy': {
            'handlers': ['console', 'syslog', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'oauthlib': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

LOGGER.warning("Running with database '%s' (backend=%s)", DATABASES['default']['NAME'],
               DATABASES['default']['ENGINE'])

TEST = False
if 'test' in sys.argv:
    # LOGGING = None
    TEST = True

if DEBUG is True:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

# Load subapps's INSTALLED_APPS
for app in INSTALLED_APPS:
    if app.startswith('supervisr') and \
        not app.startswith('supervisr.core.'):
        app_package = '.'.join(app.split('.')[:-2])
        try:
            app_settings = importlib.import_module("%s.settings" % app_package)
            INSTALLED_APPS.extend(getattr(app_settings, 'INSTALLED_APPS', []))
            MIDDLEWARE.extend(getattr(app_settings, 'MIDDLEWARE', []))
            AUTHENTICATION_BACKENDS.extend(getattr(app_settings, 'AUTHENTICATION_BACKENDS', []))
            DATABASE_ROUTERS.extend(getattr(app_settings, 'DATABASE_ROUTERS', []))
        except ImportError:
            pass
