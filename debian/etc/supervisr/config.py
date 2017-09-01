"""
Supervisr default local settings
"""
from os import path

from supervisr.core.utils import (db_settings_from_dbconfig, import_dir,
                                  read_simple)

LOCAL_BASE = path.join((path.dirname(__file__)) + '/')

DEBUG = False

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

DATABASES = {
    'default': db_settings_from_dbconfig(path.join(LOCAL_BASE, 'database-config')),
}

import_dir(path.join(LOCAL_BASE, 'conf.d'), lambda module: globals()[key] = value if not key.startswith('__') and not key.endswith('__') for key, value in module.__dict__.items())
