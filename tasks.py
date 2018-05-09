"""Supervisr Invoke Tasks"""
import os
from importlib import import_module

from invoke import Collection

import supervisr.cli.tasks

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supervisr.core.settings")
os.environ.setdefault("SUPERVISR_LOCAL_SETTINGS", "supervisr.local_settings")

# pylint: disable=invalid-name
namespace = Collection()
for submod in dir(supervisr.cli.tasks):
    if not submod.startswith('_'):
        if 'ci' in submod and os.getenv('SUPERVISR_PACKAGED', "False").title() == 'True':
            continue
        namespace.add_collection(
            Collection.from_module(import_module('supervisr.cli.tasks.%s' % submod)))
