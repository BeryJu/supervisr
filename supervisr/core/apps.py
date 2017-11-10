"""
Supervisr core app config
"""

from __future__ import unicode_literals

import uuid
import importlib
import logging
import os

import pkg_resources
from django.apps import AppConfig
from django.conf import settings
from django.core.cache import cache
from django.db.utils import OperationalError, ProgrammingError
from pip.req import parse_requirements

from supervisr.core.thread.background import BackgroundThread

LOGGER = logging.getLogger(__name__)


class SupervisrAppConfig(AppConfig):
    """
    Base AppConfig Class that logs when it's loaded
    """

    init_modules = ['signals', 'models']
    admin_url_name = 'admin-mod_default'
    view_user_settings = None
    navbar_enabled = lambda self, request: False
    title_moddifier = lambda self, label, request: label.title()

    def __init__(self, *args, **kwargs):
        """
        Set app Label based on full name
        """
        self.label = self.name.replace('.', '/')
        super(SupervisrAppConfig, self).__init__(*args, **kwargs)

    def ready(self):
        #self.check_requirements()
        self.load_init()
        self.merge_settings()
        self.run_ensure_settings()
        super(SupervisrAppConfig, self).ready()

    # pylint: disable=no-self-use
    def clear_cache(self):
        """
        Clear cache on startup
        """
        cache.clear()
        LOGGER.info("Successfully cleared Cache")

    # pylint: disable=no-self-use
    def run_ensure_settings(self):
        """
        Make sure settings defined in `ensure_settings` are theere
        """
        try:
            from supervisr.core.models import Setting
            items = self.ensure_settings()
            namespace = '.'.join(self.__module__.split('.')[:-1])
            for key, defv in items.items():
                Setting.objects.get_or_create(
                    key=key,
                    namespace=namespace,
                    defaults={'value': defv})
            if items:
                LOGGER.info("Ensured %d settings", len(items))
        except (OperationalError, ProgrammingError):
            pass

    def ensure_settings(self):
        """
        By Default ensure no settings
        """
        return {}

    def load_init(self):
        """
        Load initial modules for decorators
        """
        LOGGER.info("Loaded %s", self.name)
        for module in self.init_modules:
            if importlib.util.find_spec("%s.%s" % (self.name, module)) is not None:
                LOGGER.info("Loaded %s.%s", self.name, module)
                importlib.import_module("%s.%s" % (self.name, module))

    def check_requirements(self):
        """
        Check requirements(-dev) and see if everything is installed
        """
        def _check_file(self, path):
            # Basedir
            basedir = (os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.realpath(__file__)))))
            # Path to the this module
            subdir = os.sep.join(self.__module__.split('.')[:-1])
            # Complete path to *path
            path = os.path.join(basedir, subdir, path)

            if not os.path.isfile(path):
                # Path is not a file, assume this module has no requirements
                return False

            # Read file and parse all lines
            install_reqs = parse_requirements(path, session='hack')

            pkg_resources.require([str(x.req) for x in install_reqs])

        _check_file(self, 'requirements.txt')
        if settings.DEBUG:
            _check_file(self, 'requirements-dev.txt')

    def merge_settings(self, overwrite=False):
        """
        Load settings file and add/overwrite
        """
        blacklist = ['INSTALLED_APPS', 'MIDDLEWARE', 'SECRET_KEY']
        try:
            counter = 0
            sub_settings = importlib.import_module("%s.settings" % self.name)
            for key in dir(sub_settings):
                if not key.startswith('__') and not key.endswith('__') and key.isupper():
                    # Only overwrite if set
                    if overwrite is True or \
                        hasattr(settings, key) is False and \
                        key not in blacklist:
                        value = getattr(sub_settings, key)
                        setattr(settings, key, value)
                        counter += 1
            if counter > 0:
                LOGGER.info("Overwrote %s settings for %s", counter, self.name)
        except ImportError:
            pass # ignore non-existant modules


class SupervisrCoreConfig(SupervisrAppConfig):
    """
    Supervisr core app config
    """

    name = 'supervisr.core'
    label = 'supervisr/core'
    init_modules = [
        'signals',
        'events',
        'mailer',
        'models',
        'providers.base',
        'providers.domain',
        'providers.internal',
    ]
    navbar_title = 'Core'
    verbose_name = 'Supervisr Core'

    def ready(self):
        super(SupervisrCoreConfig, self).ready()
        self.clear_cache()
        BackgroundThread().start()
        # Set external_domain on raven
        from supervisr.core.models import Setting
        settings.RAVEN_CONFIG['tags']['external_domain'] = Setting.get('domain')

    def ensure_settings(self):
        """ensure Core settings"""
        return {
            'signup:enabled': True,
            'password_reset:enabled': True,
            'banner:enabled': False,
            'banner:level': 'info',
            'banner:message': '',
            'branding': 'supervisr',
            'branding:icon': '',
            'domain': 'http://localhost/',
            'maintenancemode': False,
            'password:filter': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])'
                               r'[A-Za-z\d$@$!%*?&]{8,}',
            'password:filter:description': 'Minimum 8 characters at least 1 Uppercase Alphabet, 1'
                                           'Lowercase Alphabet, 1 Number and 1 Special Character',
            'recaptcha:private': '',
            'recaptcha:public': '',
            'install_id': uuid.uuid4(),
        }
