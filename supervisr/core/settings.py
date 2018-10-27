""" Static settings for supervisr and supervisr.* """
# flake8: noqa
####################################################################################################
####################################################################################################
###
### You should not edit this file. Settings can be changed by editing /etc/supervisr/config.yml
### (Debian) or supervisr/environments/local.yml (source)
###
####################################################################################################
####################################################################################################





































import importlib
import os
import sys

import raven
from django.contrib import messages

from supervisr.core.utils.config import CONFIG

# WARNING!
# This can only be changed before the first `migrate` is run
# If you change this afterwards, it may cause serious damage!
SYSTEM_USER_NAME = 'supervisr'
USER_PROFILE_ID_START = 5000
FOOTER_EXTRA_LINKS = CONFIG.get('footer')
# Structure: see default.yml

REMEMBER_SESSION_AGE = 60 * 60 * 24 * 30  # One Month

NOCAPTCHA = True

REQUEST_APPROVAL_PROMPT = 'auto'

CHERRYPY_SERVER = {}
for name, namespace in CONFIG.get('http').items():
    CHERRYPY_SERVER[name] = {
        'server.socket_host': CONFIG.get('listen', '0.0.0.0'), # nosec
        'server.socket_port': CONFIG.get('port', 8000),
        'server.thread_pool': CONFIG.get('threads', 30),
        'log.screen': False,
        'log.access_file': '',
        'log.error_file': '',
    }

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'captcha',
    'supervisr.core',
    'formtools',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'raven.contrib.django.raven_compat',
] + CONFIG.get('installed_apps', [])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = BASE_DIR + '/data'
STATIC_ROOT = DATA_DIR + '/static'
MEDIA_ROOT = DATA_DIR + '/media'
CACHE_DIR = DATA_DIR + '/cache'
# Make sure all needed directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
SECRET_KEY = CONFIG.get('secret_key',
                        '_k*@6h2u2@q-dku57hhgzb7tnx*ba9wodcb^s9g0j59@=y(@_o') # noqa Debug
DEBUG = CONFIG.get('debug', True)
CORS_ORIGIN_ALLOW_ALL = DEBUG
CORS_ORIGIN_WHITELIST = CONFIG.get('domains')
ALLOWED_HOSTS = CONFIG.get('domains')

LANGUAGE_CODE = 'en-us'
TIME_ZONE = CONFIG.get('timezone', 'UTC')
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
LOGIN_REDIRECT_URL = 'user-index'
LOGIN_URL = 'account-login'

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
    'supervisr.core.middleware.statistic_middleware.statistic_middleware'
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

DATABASES = {}
for db_alias, db_config in CONFIG.get('databases').items():
    DATABASES[db_alias] = {
        'ENGINE': db_config.get('engine'),
        'HOST': db_config.get('host'),
        'NAME': db_config.get('name'),
        'USER': db_config.get('user'),
        'PASSWORD': db_config.get('password'),
        'OPTIONS': db_config.get('options', {}),
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


# Apply redis settings from local_settings
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://%s" % CONFIG.get('redis'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
DJANGO_REDIS_IGNORE_EXCEPTIONS = True
DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True

SESSION_CACHE_ALIAS = "default"


# Celery settings
# Add a 10 minute timeout to all Celery tasks.
CELERY_TASK_SOFT_TIME_LIMIT = 600
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {}
CELERY_CREATE_MISSING_QUEUES = True
CELERY_TASK_DEFAULT_QUEUE = 'supervisr'
CELERY_BROKER_URL = 'redis://%s' % CONFIG.get('redis')
CELERY_RESULT_BACKEND = 'redis://%s' % CONFIG.get('redis')


with CONFIG.cd('email'):
    EMAIL_HOST = CONFIG.get('host', default='localhost')
    EMAIL_PORT = CONFIG.get('port', default=25)
    EMAIL_HOST_USER = CONFIG.get('user', default='')
    EMAIL_HOST_PASSWORD = CONFIG.get('password', default='')
    EMAIL_USE_TLS = CONFIG.get('use_tls', default=False)
    EMAIL_USE_SSL = CONFIG.get('use_ssl', default=False)
    EMAIL_FROM = CONFIG.get('from')
    SERVER_EMAIL = CONFIG.get('from')

ENVIRONMENT = 'production' if DEBUG is False else 'development'

# Try to get version from git, otherwise get from setup.py
try:
    VERSION = raven.fetch_git_sha(os.path.dirname(os.pardir))[:8]
except raven.exceptions.InvalidGitRepository:
    from supervisr import __version__  # pylint: disable=no-name-in-module, useless-suppression
    VERSION = __version__

RAVEN_CONFIG = {
    'dsn': CONFIG.get('sentry', ''),
    'release': VERSION,
    'environment': ENVIRONMENT,
    'tags': {'external_domain': ''}
}

LOG_HANDLERS = ['console', 'syslog', 'file', 'sentry']

with CONFIG.cd('log'):
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'verbose': {
                'format': ('%(asctime)s %(levelname)-8s %(name)-55s '
                           '%(funcName)-20s %(message)s'),
            },
            'color': {
                '()': 'colorlog.ColoredFormatter',
                'format': ('%(log_color)s%(asctime)s %(levelname)-8s %(name)-55s '
                           '%(funcName)-20s %(message)s'),
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
                'level': CONFIG.get('level').get('console'),
                'class': 'logging.StreamHandler',
                'formatter': 'color',
            },
            'sentry': {
                'level': 'ERROR',
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            },
            'syslog': {
                'level': CONFIG.get('level').get('file'),
                'class': 'logging.handlers.SysLogHandler',
                'formatter': 'verbose',
                'address': (CONFIG.get('syslog').get('host'),
                            CONFIG.get('syslog').get('port'))
            },
            'file': {
                'level': CONFIG.get('level').get('file'),
                'class': 'logging.FileHandler',
                'formatter': 'verbose',
                'filename': CONFIG.get('file').get(
                    os.environ.get('SUPERVISR_COMPONENT', 'web').lower()),
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
            'flower': {
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

TEST = False
TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
TEST_OUTPUT_VERBOSE = 2

TEST_OUTPUT_FILE_NAME = 'unittest.xml'

if any('test' in arg for arg in sys.argv):
    LOGGING = None
    TEST = True

if DEBUG is True:
    ALLOWED_HOSTS += ['127.0.0.1']
    RAVEN_CONFIG['dsn'] = ''
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')


# Load subapps's INSTALLED_APPS
for _app in INSTALLED_APPS:
    if _app.startswith('supervisr') and \
            not _app.startswith('supervisr.core'):
        if 'apps' in _app:
            _app = '.'.join(_app.split('.')[:-2])
        try:
            app_settings = importlib.import_module("%s.settings" % _app)
            INSTALLED_APPS.extend(getattr(app_settings, 'INSTALLED_APPS', []))
            MIDDLEWARE.extend(getattr(app_settings, 'MIDDLEWARE', []))
            AUTHENTICATION_BACKENDS.extend(getattr(app_settings, 'AUTHENTICATION_BACKENDS', []))
            DATABASE_ROUTERS.extend(getattr(app_settings, 'DATABASE_ROUTERS', []))
            CELERY_BEAT_SCHEDULE.update(getattr(app_settings, 'CELERY_BEAT_SCHEDULE', {}))
        except ImportError:
            pass
