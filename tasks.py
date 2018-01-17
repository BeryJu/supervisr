"""
Supervisr Invoke Tasks
"""
import os
from invoke import Program, Collection
from supervisr import __version__
from importlib import import_module
import supervisr._tasks

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supervisr.core.settings")
os.environ.setdefault("SUPERVISR_LOCAL_SETTINGS", "supervisr.local_settings")

namespace = Collection()
for submod in dir(supervisr._tasks):
    if not submod.startswith('_'):
        namespace.add_collection(
            Collection.from_module(import_module('supervisr._tasks.%s' % submod)))
