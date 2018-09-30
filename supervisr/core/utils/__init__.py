"""Supervisr Core utils"""

import base64
import logging
import socket
from importlib import import_module
from urllib.parse import urlparse
from uuid import uuid4

import redis
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.core.management.base import OutputWrapper
from django.db import DEFAULT_DB_ALIAS
from django.db.utils import ConnectionDoesNotExist, OperationalError
from django.http import HttpRequest
from django.template import Context, Template, loader

from supervisr.core.apps import SupervisrAppConfig, SupervisrCoreConfig
from supervisr.core.utils.logger import SUCCESS

LOGGER = logging.getLogger(__name__)


def get_remote_ip(request: HttpRequest) -> str:
    """Return the remote's IP"""
    if not request:
        return '0.0.0.0'  # nosec
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


def render_from_string(template: str, ctx: Context) -> str:
    """Render template from string to string"""
    template = Template(template)
    return template.render(ctx)


def render_to_string(template_path: str, ctx: Context) -> str:
    """Render a template to string"""
    template = loader.get_template(template_path)
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


def b64encode(*args):
    """String wrapper around b64encode to removie binary fuckery"""
    return base64.b64encode(str.encode(''.join(args))).decode()


def b64decode(*args):
    """String wrapper around b64decode to remove binary fuckery"""
    return base64.b64decode(''.join(args)).decode()


def check_db_connection(connection_name: str = DEFAULT_DB_ALIAS) -> bool:
    """Check if a database connection can be made

    Args:
        connection_name: Name of the Django database connection Name.

    Returns:
        bool: True if connection could be made, otherwise False.
    """
    from django.db import connections
    try:
        db_conn = connections[connection_name]
        db_conn.cursor()
    except (OperationalError, ConnectionDoesNotExist):
        return False
    else:
        return True


def check_redis_connection() -> bool:
    """Check if redis server can be reached"""
    client = redis.Redis.from_url(settings.CELERY_BROKER_URL)
    try:
        return client.ping()
    except (redis.exceptions.ConnectionError,
            redis.exceptions.BusyLoadingError):
        return False


def get_db_server_version(connection_name: str = DEFAULT_DB_ALIAS, default: str = '') -> str:
    """Return the Version of the Database server"""
    from django.db import connections
    db_conn = connections[connection_name]
    cursor = db_conn.cursor()
    try:
        cursor.execute('SELECT VERSION();')
        return cursor.fetchone()[0]
    except OperationalError:
        return default
    finally:
        cursor.close()


def messages_add_once(request, level, text, **kwargs):
    """Add text to messages, but make sure no duplicates exist"""
    exists = False
    storage = messages.get_messages(request)
    for msg in storage:
        if msg.message == text:
            exists = True
    storage.used = False
    if not exists:
        return messages.add_message(request, level, text, **kwargs)
    return False


def is_url_absolute(url):
    """Check if domain is absolute to prevent user from being redirect somewhere else"""
    return bool(urlparse(url).netloc)


def is_database_synchronized(database=DEFAULT_DB_ALIAS):
    """Check if database has migrations pending"""
    from django.db import connections
    from django.db.migrations.executor import MigrationExecutor
    connection = connections[database]
    connection.prepare_database()
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    return False if executor.migration_plan(targets) else True


class LogOutputWrapper(OutputWrapper):
    """Output wrapper for django management commands to use LOGGER instead of direct print"""

    level = SUCCESS

    def __init__(self):
        super().__init__(out=None)

    def write(self, msg, style_func=None, ending=None):
        ending = self.ending if ending is None else ending
        if ending and not msg.endswith(ending):
            msg += ending
        style_func = style_func or self.style_func
        # Trim trailing \n off
        if msg.endswith('\n'):
            msg = msg[:-1]
        LOGGER.log(self.level, style_func(msg))
