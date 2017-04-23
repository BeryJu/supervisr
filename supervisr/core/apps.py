"""
Supervisr core app config
"""

from __future__ import unicode_literals

import importlib
import logging
import subprocess

from django.apps import AppConfig
from django.conf import settings

LOGGER = logging.getLogger(__name__)


class SupervisrAppConfig(AppConfig):
    """
    Base AppConfig Class that logs when it's loaded
    """

    init_modules = ['signals', 'events', 'models']
    admin_url_name = 'admin-mod_default'
    navbar_title = None
    view_user_settings = None

    def ready(self):
        self.load_init()
        self.merge_settings()
        super(SupervisrAppConfig, self).ready()

    def load_init(self):
        """
        Load initial modules for decorators
        """
        LOGGER.info("Loaded %s", self.name)
        for module in self.init_modules:
            try:
                importlib.import_module("%s.%s" % (self.name, module))
                LOGGER.info("Loaded %s.%s", self.name, module)
            except ImportError:
                pass # ignore non-existant modules

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
    init_modules = ['signals', 'events', 'mailer', 'models']
    navbar_title = 'Core'

    def ready(self):
        # Read this commit's shortened hash if git is in the path
        try:
            current_hash = subprocess.Popen(['git', 'log', '--pretty=format:%h', '-n 1'],
                                            stdout=subprocess.PIPE).communicate()[0]
            settings.VERSION_HASH = current_hash
        except (OSError, IOError):
            settings.VERSION_HASH = b'dev'
        super(SupervisrCoreConfig, self).ready()
