"""Supervisr Core utils"""

import base64
import logging
import socket
from glob import glob
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from time import time as timestamp
from uuid import uuid4

from django.apps import apps
from django.contrib import messages
from django.core.cache import cache
from django.http import HttpRequest
from django.shortcuts import render
from django.template import Context, Template, loader
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from supervisr.core.apps import SupervisrAppConfig, SupervisrCoreConfig

LOGGER = logging.getLogger(__name__)


def get_remote_ip(request: HttpRequest) -> str:
    """Return the remote's IP"""
    if not request:
        return '0.0.0.0'
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        return request.META.get('HTTP_X_FORWARDED_FOR')
    return request.META.get('REMOTE_ADDR')

def uuid():
    """Return a UUID as string with just alphanumeric-chars"""
    return str(uuid4()).replace('-', '').upper()

def get_reverse_dns(dev_ip):
    """Does a reverse DNS lookup and returns the first IP"""
    try:
        rev = socket.gethostbyaddr(dev_ip)
        if rev:
            return rev[0]
    except (socket.herror, TypeError, IndexError):
        pass
    return ''

def do_404(request, message=None):
    """Boilerplate to return a 404 message"""
    return render(request, 'common/error.html', {
        'code': 404,
        'message': _(message) if message is not None else None
    }, status=404)

def render_from_string(tmpl: str, ctx: Context) -> str:
    """Render template from string to string"""
    template = Template(tmpl)
    return template.render(ctx)

def render_to_string(tmpl: str, ctx: Context) -> str:
    """Render a template to string"""
    template = loader.get_template(tmpl)
    return template.render(ctx)

def get_apps(exclude=None):
    """Get a list of all installed apps"""
    if exclude is None:
        exclude = [SupervisrCoreConfig]
    app_list = []
    for app in apps.get_app_configs():
        if isinstance(app, SupervisrAppConfig):
            is_excluded = False
            for exclusion in exclude:
                if isinstance(app, exclusion):
                    is_excluded = True
            if not is_excluded:
                app_list.append(app)
    return app_list

def get_app_labels():
    """Cache all installed apps and return the list"""
    cache_key = 'core:app_labels'
    if not cache.get(cache_key):
        # Make a list of all short names for all apps
        app_cache = []
        for app in get_apps():
            app_cache.append(app.label)
        cache.set(cache_key, app_cache, 1000)
        return app_cache
    return cache.get(cache_key) # pragma: no cover

def class_to_path(cls):
    """Turn Class (Class or instance) into module path"""
    return '%s.%s' % (cls.__module__, cls.__name__)

def path_to_class(path):
    """Import module and return class"""
    if not path:
        return None
    parts = path.split('.')
    package = '.'.join(parts[:-1])
    _class = getattr(import_module(package), parts[-1])
    return _class

def db_settings_from_dbconfig(config_path):
    """Generate Django DATABASE dict from dbconfig file"""
    db_config = {}
    with open(config_path, 'r') as file:
        contents = file.read().split('\n')
        for line in contents:
            if line.startswith('#') or line == '':
                continue
            key, value = line.split('=')
            value = value[1:-1]
            if key == 'dbuser':
                db_config['USER'] = value
            elif key == 'dbpass':
                db_config['PASSWORD'] = value
            elif key == 'dbname':
                db_config['NAME'] = value
            elif key == 'dbserver':
                db_config['HOST'] = value
            elif key == 'dbport':
                db_config['PORT'] = value
            elif key == 'dbtype':
                if value == 'mysql':
                    db_config['ENGINE'] = 'django.db.backends.mysql'
                    db_config['OPTIONS'] = {
                        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
                    }
                elif value == 'pgsql':
                    db_config['ENGINE'] = 'django.db.backends.postgresql'
        return db_config

def read_simple(path, mode='r'):
    """Simple wrapper for file reading"""
    with open(path, mode) as file:
        return file.read()

def import_dir(directory):
    """Import every file in a direct and call callback for each"""
    files = glob(directory+'/*.py', recursive=True)
    modules = []
    for file in files:
        spec = spec_from_file_location("", file)
        modules.append(module_from_spec(spec))
    return modules

def b64encode(*args):
    """String wrapper around b64encode to removie binary fuckery"""
    return base64.b64encode(str.encode(''.join(args))).decode()

def b64decode(*args):
    """String wrapper around b64decode to remove binary fuckery"""
    return base64.b64decode(''.join(args)).decode()

def check_db_connection(connection_name: str = 'default') -> bool:
    """Check if a database connection can be made

    Args:
        connection_name: Name of the Django database connection Name.

    Returns:
        bool: True if connection could be made, otherwise False.
    """
    from django.db import connections
    from django.db.utils import OperationalError, ConnectionDoesNotExist
    try:
        db_conn = connections[connection_name]
        db_conn.cursor()
    except (OperationalError, ConnectionDoesNotExist):
        return False
    else:
        return True

def messages_add_once(request, level, text, **kwargs):
    """Add text to messages, but make sure no duplicates exist"""
    exists = False
    storage = messages.get_messages(request)
    for msg in storage:
        if msg.message == text:
            exists = True
    storage.used = False
    if not exists:
        return messages.add_message(request, level, mark_safe(text), **kwargs)
    return False
