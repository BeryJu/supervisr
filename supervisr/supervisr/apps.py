"""
Supervisr core app config
"""

from __future__ import unicode_literals

import importlib
import logging
import os
import subprocess

from django.apps import AppConfig
from django.conf import settings

LOGGER = logging.getLogger(__name__)


class SupervisrAppConfig(AppConfig):
    """
    Base AppConfig Class that logs when it's loaded
    """

    init_modules = ['signals']
    admin_url_name = 'admin-mod_default'
    inject_middleware = []

    def __init__(self, *args, **kwargs):
        settings.MIDDLEWARE.extend(self.inject_middleware)
        super(SupervisrAppConfig, self).__init__(*args, **kwargs)

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
        try:
            counter = 0
            sub_settings = importlib.import_module("%s.settings" % self.name)
            for key in dir(sub_settings):
                if not key.startswith('__') and not key.endswith('__'):
                    # Only overwrite if set
                    if overwrite is True or hasattr(settings, key) is False:
                        value = getattr(sub_settings, key)
                        setattr(settings, key, value)
                        counter += 1
            LOGGER.info("Overwrote %s settings for %s", counter, self.name)
        except ImportError:
            pass # ignore non-existant modules


class SupervisrCoreConfig(SupervisrAppConfig):
    """
    Supervisr core app config
    """

    name = 'supervisr'
    init_modules = ['signals', 'events', 'mailer', 'models']

    def ready(self):
        # Looks ugly, but just goes two dirs up and gets CHANGELOG.md
        current_dir = os.path.dirname(__file__)
        two_up = os.path.split(os.path.split(current_dir)[0])[0]
        changelog_file = os.path.join(two_up, 'CHANGELOG.md')
        try:
            file = open(changelog_file, 'r')
            settings.CHANGELOG = file.read()
            file.close()
        except (OSError, IOError):
            settings.CHANGELOG = 'Failed to load Changelog.md'
        # Read this commit's shortened hash if git is in the path
        try:
            current_hash = subprocess.Popen(['git', 'log', '--pretty=format:%h', '-n 1'],
                                            stdout=subprocess.PIPE).communicate()[0]
            settings.VERSION_HASH = current_hash
        except (OSError, IOError):
            settings.VERSION_HASH = b'dev'
        super(SupervisrCoreConfig, self).ready()
