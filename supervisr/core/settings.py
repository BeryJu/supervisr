""" Static settings for supervisr and supervisr.* """
# flake8: noqa
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
FOOTER_EXTRA_LINKS = []
# Structure of
# {
# text: "",
# view: "",
# url: "",
# }

REMEMBER_SESSION_AGE = 60 * 60 * 24 * 30  # One Month

LOGGER = logging.getLogger(__name__)

NOCAPTCHA = True

CORS_ORIGIN_ALLOW_ALL = True
REQUEST_APPROVAL_PROMPT = 'auto'

CHERRYPY_SERVER = {
    'socket_host': '0.0.0.0', # nosec
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
    'supervisr.mod.provider.nix_dns.apps.SupervisrModProviderNixDNSConfig',
    'supervisr.mod.provider.debug.apps.SupervisrModProviderDebugConfig',
    'supervisr.mail.apps.SupervisrMailConfig',
    'supervisr.static.apps.SupervisrStaticConfig',
    'supervisr.mod.web_proxy.apps.SupervisrModWebProxyConfig',
    'supervisr.mod.beacon.apps.SupervisrModBeaconConfig',
    'supervisr.mod.auth.ldap.apps.SupervisrModAuthLDAPConfig',
    'supervisr.mod.auth.saml.idp.apps.SupervisrModAuthSAMLProvider',
    'supervisr.mod.auth.oauth.provider.apps.SupervisrModAuthOAuthProviderConfig',
    'supervisr.mod.auth.oauth.client.apps.SupervisrModAuthOAuthClientConfig',
    'supervisr.mod.tfa.apps.SupervisrModTFAConfig',
    'supervisr.mod.stats.influx.apps.SupervisrModStatInfluxConfig',
    'formtools',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'raven.contrib.django.raven_compat',
    'django_celery_results',
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))) + "/static"
MEDIA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/media"
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

REDIS = 'localhost'

# Celery settings
# Add a 10 minute timeout to all Celery tasks.
CELERY_TASK_SOFT_TIME_LIMIT = 600
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {}
CELERY_CREATE_MISSING_QUEUES = True

# Settings are taken from DB, these are dev keys as per
# https://developers.google.com/recaptcha/docs/faq
RECAPTCHA_PUBLIC_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
RECAPTCHA_PRIVATE_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'

INTERNAL_IPS = ['127.0.0.1']

MIDDLEWARE = [
    # Load DeployPage first so we can save unnecessary errores
    'supervisr.core.middleware.deploy_page_middleware.deploy_page',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
    'supervisr.core.middleware.redirect_middleware.redirect_middleware',
    'supervisr.core.middleware.impersonate_middleware.impersonate',
    'supervisr.core.middleware.permanent_message_middleware.permanent_message',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
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

CSRF_COOKIE_NAME = 'supervisr_csrf'
SESSION_COOKIE_NAME = 'supervisr_sessionid'

API_KEY_PARAM = 'sv-api-key'

WSGI_APPLICATION = 'supervisr.core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dev.db',
    }
}

AUTH_USER_MODEL = 'supervisr_core.User'

AUTHENTICATION_BACKENDS = [
    'supervisr.core.auth.EmailBackend',
    'supervisr.core.auth.APIKeyBackend',
]

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
LOG_LEVEL_CONSOLE = 'DEBUG' if DEBUG else 'INFO'
LOG_FILE = '/dev/null'

LOG_SYSLOG_HOST = '127.0.0.1'
LOG_SYSLOG_PORT = 514

SENTRY_DSN = ''
sys.path.append('/etc/supervisr')


def load_local_settings(module_path):
    """Load module *mod* and apply contents to ourselves"""
    try:
        loaded_module = importlib.import_module(module_path, package=None)
        for key, value in loaded_module.__dict__.items():
            if not key.startswith('__') and not key.endswith('__'):
                globals()[key] = value
        LOGGER.warning("Loaded '%s' as local_settings", module_path)
        return True
    except (ImportError, PermissionError) as exception:
        LOGGER.info('Not loaded %s because %s', module_path, exception)
        return False

for _module in [os.environ.get('SUPERVISR_LOCAL_SETTINGS', 'supervisr.local_settings'), 'config']:
    if load_local_settings(_module):
        break

# Apply redis settings from local_settings
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://%s" % REDIS,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
DJANGO_REDIS_IGNORE_EXCEPTIONS = True
DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True

SESSION_CACHE_ALIAS = "default"

CELERY_TASK_DEFAULT_QUEUE = 'supervisr'
CELERY_BROKER_URL = 'redis://%s' % REDIS
CELERY_RESULT_BACKEND = 'django-db'

SERVER_EMAIL = EMAIL_FROM
ENVIRONMENT = 'production' if DEBUG is False else 'development'

# Try to get version from git, otherwise get from setup.py
try:
    VERSION = raven.fetch_git_sha(os.path.dirname(os.pardir))[:8]
except raven.exceptions.InvalidGitRepository:
    from supervisr import __version__  # pylint: disable=no-name-in-module, useless-suppression
    VERSION = __version__

RAVEN_CONFIG = {
    'dsn': SENTRY_DSN,
    'release': VERSION,
    'environment': ENVIRONMENT,
    'tags': {'external_domain': ''}
}

LOG_HANDLERS = ['console', 'syslog', 'file', 'sentry']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': ('[%(asctime)s] %(levelname)s '
                       '[%(name)s::%(funcName)s::%(lineno)s] %(message)s'),
        },
        'verbose': {
            'format': ('%(process)-5d %(thread)d %(name)-45s '
                       '%(levelname)-8s %(funcName)-20s %(message)s'),
        },
        'color': {
            '()': 'colorlog.ColoredFormatter',
            'format': ('%(log_color)s%(process)-5d %(thread)d %(name)-45s '
                       '%(levelname)-8s %(funcName)-20s %(message)s'),
            'log_colors': {
                'DEBUG': 'bold_black',
                'INFO': 'white',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
                'SUCCESS': 'green',
            },
        }
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL_CONSOLE,
            'class': 'logging.StreamHandler',
            'formatter': 'color',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'syslog': {
            'level': LOG_LEVEL_FILE,
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'verbose',
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
            'handlers': LOG_HANDLERS,
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': LOG_HANDLERS,
            'level': 'INFO',
            'propagate': True,
        },
        'tasks': {
            'handlers': LOG_HANDLERS,
            'level': 'DEBUG',
            'propagate': True,
        },
        'cherrypy': {
            'handlers': LOG_HANDLERS,
            'level': 'DEBUG',
            'propagate': True,
        },
        'oauthlib': {
            'handlers': LOG_HANDLERS,
            'level': 'DEBUG',
            'propagate': True,
        },
        'celery': {
            'handlers': LOG_HANDLERS,
            'level': 'WARNING',
            'propagate': True,
        },
    }
}

LOGGER.warning("Running with database '%s' (backend=%s)", DATABASES['default']['NAME'],
               DATABASES['default']['ENGINE'])

TEST = False
TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
TEST_OUTPUT_VERBOSE = 2

TEST_OUTPUT_FILE_NAME = 'unittest.xml'

if 'test' in sys.argv:
    LOGGING = None
    TEST = True

if DEBUG is True:
    RAVEN_CONFIG['dsn'] = ''
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')


# Load subapps's INSTALLED_APPS
for _app in INSTALLED_APPS:
    if _app.startswith('supervisr') and \
            not _app.startswith('supervisr.core.'):
        _app_package = '.'.join(_app.split('.')[:-2])
        try:
            app_settings = importlib.import_module("%s.settings" % _app_package)
            INSTALLED_APPS.extend(getattr(app_settings, 'INSTALLED_APPS', []))
            MIDDLEWARE.extend(getattr(app_settings, 'MIDDLEWARE', []))
            AUTHENTICATION_BACKENDS.extend(getattr(app_settings, 'AUTHENTICATION_BACKENDS', []))
            DATABASE_ROUTERS.extend(getattr(app_settings, 'DATABASE_ROUTERS', []))
            CELERY_BEAT_SCHEDULE.update(getattr(app_settings, 'CELERY_BEAT_SCHEDULE', {}))
        except ImportError:
            pass
