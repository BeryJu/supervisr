"""
MySQL Local settings
"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'supervisr_test',
        'USER': 'root',
        'PASSWORD': 'EK-5jnKfjrGRm<77',
        'HOST': 'mysql',
        'PORT': '',
        'OPTIONS': {
            'init_command': """
            SET sql_mode='STRICT_TRANS_TABLES',
            character_set_connection=utf8,
            collation_connection=utf8_unicode_ci
            """
        }
    }
}
