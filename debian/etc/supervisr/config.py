"""
Supervisr default local settings
"""
from os import path

from supervisr.core.utils import db_settings_from_dbconfig

LOCAL_BASE = path.join((path.dirname(__file__)) + '/')

DEBUG = False

# Never share this key with anyone.
# If you change this key, you also have to clear your database otherwise things break.
SECRET_KEY = ''
with open(path.join(LOCAL_BASE, 'secret_key'), 'r') as f:
    SECRET_KEY = f.read()

LOG_LEVEL_CONSOLE = 'WARNING'
LOG_LEVEL_FILE = 'INFO'
LOG_FILE = '/var/log/supervisr/supervisr.log'

DATABASES = {
    'default': db_settings_from_dbconfig(path.join(LOCAL_BASE, 'database-config')),
}
