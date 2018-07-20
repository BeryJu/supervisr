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
            'charset': 'UTF8MB4',
            'sql_mode': 'STRICT_TRANS_TABLES',
            'init_command': "ALTER DATABASE supervisr_test "
                            "CHARACTER SET UTF8MB4 COLLATE utf8mb4_bin;"
        }
    }
}
