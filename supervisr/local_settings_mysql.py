"""
MySQL Local settings
"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'supervisr_test',
        'USER': 'newuser',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES',character_set_connection=utf8,collation_connection=utf8_unicode_ci"
        }
    }
}
