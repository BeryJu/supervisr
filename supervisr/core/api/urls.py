"""
Supervisr API Urls
"""

import importlib
import inspect
import logging
import os
import os.path
from glob import glob

from django.conf import settings
from django.conf.urls import include, url

LOGGER = logging.getLogger(__name__)


def auto_discover():
    """Automatically discover API modules and return urlpatterns for them"""
    urlpatterns = []
    # We need this local_base_dir for non-packaged modules
    # This gets the absolute path to three directories up
    # since this should be called from $root/api/urls.py
    local_base_dir = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(inspect.getmodule(inspect.stack()[1][0]).__file__))))
    urls_module = inspect.getmodule(inspect.stack()[1][0]).__name__
    # Get the base API module
    base = importlib.import_module('.'.join(urls_module.split('.')[:-1]))
    api_dir = os.path.dirname(base.__file__)
    # Find all subdirectories matching v[0-9]
    versions = glob("%s/v[0-9]*/__init__.py" % api_dir)
    # Keep a hash for default url
    version_hash = {}
    for module_path in versions:
        # We want the urls module, not the version module itself
        module_path = module_path.replace('__init__', 'urls') \
                                 .replace('./', '') \
                                 .replace('.py', '') \
                                 .replace(settings.BASE_DIR, 'supervisr') \
                                 .replace(local_base_dir, '') \
                                 .replace(os.sep, '.')
        # Since absolute paths start with a /, which gets converted to a
        # dot above, we need to remove this here to make it a non-relative
        # import
        if module_path[0] == '.':
            module_path = module_path[1:]
        # This is just a sanity check to see if the module is importable
        importlib.import_module(module_path)
        version_name = module_path.split('.')[-2]  # get the second last module name (version)
        namespace = '_'.join(module_path.split('.')[:-1])
        urlpatterns.append(url('%s/' % version_name, include((module_path, namespace),
                                                             namespace=namespace)))
        # get numerical api version to determine default
        version = int(version_name.replace('v', ''))
        # append to version_hash
        default_namespace = namespace.replace(version_name, 'default')
        version_hash[version] = url('', include((module_path, default_namespace),
                                                namespace=default_namespace))
        LOGGER.debug("Found API module '%s' (namespace=%s)", version_name, namespace)
    # set default to highest version
    newest = max(version_hash, key=int)
    urlpatterns.insert(0, version_hash[newest])
    LOGGER.debug("Found default API module 'v%d' (namespace=%s)", newest,
                 version_hash[newest].namespace)
    return urlpatterns


urlpatterns = auto_discover()
