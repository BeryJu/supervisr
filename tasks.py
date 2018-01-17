"""
Supervisr Invoke Tasks
"""
import os
from importlib import import_module

from invoke import Collection

import supervisr._tasks

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supervisr.core.settings")
os.environ.setdefault("SUPERVISR_LOCAL_SETTINGS", "supervisr.local_settings")

# pylint: disable=invalid-name
namespace = Collection()
# pylint: disable=protected-access
for submod in dir(supervisr._tasks):
    if not submod.startswith('_'):
        namespace.add_collection(
            Collection.from_module(import_module('supervisr._tasks.%s' % submod)))
