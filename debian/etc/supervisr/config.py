"""
Supervisr default local settings
"""
from os import path

from supervisr.core.utils import (db_settings_from_dbconfig, import_dir,
                                  read_simple)

LOCAL_BASE = path.join((path.dirname(__file__)) + '/')

DEBUG = False

ADMINS = [
    ('Admin', 'admin@domain.tld'),
]
EMAIL_HOST = 'mx1.domain.tld'
EMAIL_FROM = 'Supervisr <supervisr@domain.tld>'

CHERRYPY_SERVER = {
    'socket_host': '0.0.0.0',
    'socket_port': 8000,
    'thread_pool': 30
}

# Never share this key with anyone.
# If you change this key, you also have to clear your database otherwise things break.
SECRET_KEY = read_simple(path.join(LOCAL_BASE, 'secret_key'))

LOG_LEVEL_CONSOLE = 'WARNING'
LOG_LEVEL_FILE = 'INFO'
LOG_FILE = '/var/log/supervisr/supervisr.log'

# This can be used to log messages to a remote syslog serve
#LOG_SYSLOG_HOST = '172.16.1.30'
#LOG_SYSLOG_PORT = 12239

# Set this to your GitLab API key to directly report errors to gitlab
#LOG_GITLAB_API_KEY = ''

DATABASES = {
    'default': db_settings_from_dbconfig(path.join(LOCAL_BASE, 'database-config')),
}

for module in import_dir(path.join(LOCAL_BASE, 'conf.d')):
    for key, value in module.__dict__.items():
        if not key.startswith('__') and not key.endswith('__'):
            globals()[key] = value