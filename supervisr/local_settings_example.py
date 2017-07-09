# pylint: skip-file
"""
Local settings
"""

DEBUG = False

ADMINS = [
    ('Admin', 'admin@domain.tld'),
]
EMAIL_HOST = 'mx1.domain.tld'
EMAIL_FROM = 'Supervisr <supervisr@domain.tld>'

#SYSLOG_HOST = '172.16.1.30'
#SYSLOG_PORT = 12239

SECRET_KEY = ''

CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (
    # List all domains that are going to use OAuth2
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}