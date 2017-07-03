"""
Postgres Local settings
"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'supervisr_test',
        'USER': 'supervisr',
        'PASSWORD': 'EK-5jnKfjrGRm<77',
        'HOST': 'postgres',
        'PORT': '',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}
