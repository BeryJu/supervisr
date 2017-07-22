"""
Supervisr AppLoader Utils
"""

import inspect
import logging
import os
from glob import glob
from importlib import import_module

from django.conf import settings

from supervisr.core.apps import SupervisrAppConfig

LOGGER = logging.getLogger(__name__)


def cls_path(cls):
    """
    Turn class object into dotted path
    """
    return cls.__module__+'.'+cls.__name__

def find_apps():
    """
    Find all apps in filesystem and return class objects
    """
    app_classes = []
    for app in glob("%s/**/apps.py" % settings.BASE_DIR, recursive=True):
        if 'apploader' not in app:
            app_module = import_module(path_to_mod(app))
            for _name, obj in inspect.getmembers(app_module):
                if inspect.isclass(obj) \
                    and issubclass(obj, SupervisrAppConfig) \
                    and obj != SupervisrAppConfig:
                    app_classes.append(obj)
    return app_classes

def path_to_mod(path):
    """
    Convert filesyystem path to module path
    """
    _base = os.path.abspath(settings.BASE_DIR)
    return os.path.abspath(path) \
        .replace(settings.BASE_DIR, 'supervisr') \
        .replace('\\', '.') \
        .replace('.py', '')

def load_app(app_config_path, app_config_class):
    """
    Load application
    """

    if app_config_path not in settings.INSTALLED_APPS: # pylint: disable=no-member
        settings.INSTALLED_APPS += [app_config_path, ] # pylint: disable=no-member
    # Either take explicit label or guess from class path
    if getattr(app_config_class, 'label', None) is not None:
        label = app_config_class.label
    else:
        label = app_config_path.split('.')[-3]
    # To load the new app let's reset app_configs, the dictionary
    # with the configuration of loaded apps
    LOGGER.info("DBLoaded App label=%s '%s'", label, app_config_path)
