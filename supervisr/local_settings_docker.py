# pylint: skip-file
"""Local settings for Docker containers"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'supervisr',
        'USER': 'supervisr',
        'PASSWORD': 'EK-5jnKfjrGRm<77',
        'HOST': 'db',
        'PORT': '',
        'OPTIONS': {
            'charset': 'utf8',
            'sql_mode': 'STRICT_TRANS_TABLES',
            'init_command': "ALTER DATABASE supervisr "
                            "CHARACTER SET utf8 COLLATE utf8_unicode_ci;"
        }
    }
}

REDIS = 'redis'

DEBUG = False
