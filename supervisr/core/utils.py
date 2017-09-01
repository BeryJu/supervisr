"""
Supervisr Core utils
"""

import importlib.util
import logging
import socket
from glob import glob
from importlib import import_module
from time import time as timestamp
from uuid import uuid4

from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
from django.template import loader
from django.utils.translation import ugettext as _

from supervisr.core.statistics import stat_set

LOGGER = logging.getLogger(__name__)


def get_remote_ip(req):
    """
    Return the remote's IP
    """
    if not req:
        return '0.0.0.0'
    if req.META.get('HTTP_X_FORWARDED_FOR'):
        return req.META.get('HTTP_X_FORWARDED_FOR')
    return req.META.get('REMOTE_ADDR')

def uuid():
    """
    Return a UUID as string with just alphanumeric-chars
    """
    return str(uuid4()).replace('-', '').upper()

def get_reverse_dns(dev_ip):
    """
    Does a reverse DNS lookup and returns the first IP
    """
    try:
        rev = socket.gethostbyaddr(dev_ip)
        if rev:
            return rev[0]
    except (socket.herror, TypeError, IndexError):
        return ''

def do_404(req, message=None):
    """
    Boilerplate to return a 404 message
    """
    return render(req, 'common/error.html', {
        'code': 404,
        'message': _(message) if message is not None else None
    }, status=404)

def send_admin_mail(exception, message):
    """
    Send Email to all superusers
    """
    from django.contrib.auth.models import User
    from .mailer import send_message
    emails = [x.email for x in User.objects.filter(is_superuser=True)]
    return send_message(
        recipients=emails,
        subject=_("Supervisr Error %(exception)s" % {
            'exception': exception}),
        template='email/admin_mail.html',
        template_context={'exception': exception, 'message': message})

def render_to_string(tmpl, ctx):
    """
    Render a template to string
    """
    template = loader.get_template(tmpl)
    return template.render(ctx)

def get_apps(mod_only=False):
    """
    Get a list of all installed apps
    """
    app_list = []
    for app in settings.INSTALLED_APPS:
        if app.startswith('supervisr') and \
            not app.startswith('supervisr.core'):
            if mod_only:
                if app.startswith('supervisr.mod'):
                    app_list.append(app)
            else:
                app_list.append(app)
    return app_list

def get_app_labels():
    """
    Cache all installed apps and return the list
    """
    cache_key = 'core:app_labels'
    if not cache.get(cache_key):
        # Make a list of all short names for all apps
        app_cache = []
        for app in get_apps():
            try:
                mod_new = '/'.join(app.split('.')[:-2])
                config = apps.get_app_config(mod_new)
                mod = mod_new
            except LookupError:
                mod = app.split('.')[:-2][-1]
                config = apps.get_app_config(mod)
            app_cache.append(config.label)
        cache.set(cache_key, app_cache, 1000)
        return app_cache
    return cache.get(cache_key)

def time(statistic_key):
    """
    Decorator to time a method call
    """

    def outer_wrapper(method):
        """
        Decorator to time a method call
        """
        def timed(*args, **kw):
            """
            Decorator to time a method call
            """
            time_start = timestamp()
            result = method(*args, **kw)
            time_end = timestamp()

            stat_set(statistic_key, (time_end - time_start) * 1000)
            return result

        return timed

    return outer_wrapper

def class_to_path(cls):
    """
    Turn Class (Class or instance) into module path
    """
    return '%s.%s' % (cls.__module__, cls.__name__)

def path_to_class(path):
    """
    Import module and return class
    """
    if not path:
        return None
    parts = path.split('.')
    package = '.'.join(parts[:-1])
    _class = getattr(import_module(package), parts[-1])
    return _class

def db_settings_from_dbconfig(config_path):
    """
    Generate Django DATABASE dict from dbconfig file
    """
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
    """
    Simple wrapper for file reading
    """
    with open(path, mode) as file:
        return file.read()

def import_dir(directory, callback):
    """
    Import every file in a direct and call callback for each
    """
    files = glob(directory+'/*.py', recursive=True)
    for file in files:
        spec = importlib.util.spec_from_file_location("", file)
        module = importlib.util.module_from_spec(spec)
        callback(module)
