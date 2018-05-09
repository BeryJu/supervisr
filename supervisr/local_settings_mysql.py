# pylint: skip-file
"""MySQL Local settings"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'supervisr_test',
        'USER': 'root',
        'PASSWORD': 'EK-5jnKfjrGRm<77',
        'HOST': 'mysql',
        'PORT': '',
        'OPTIONS': {
            'charset': 'utf8',
            'sql_mode': 'STRICT_TRANS_TABLES',
            'init_command': "ALTER DATABASE supervisr_test "
                            "CHARACTER SET utf8 COLLATE utf8_unicode_ci;"
        }
    }
}
