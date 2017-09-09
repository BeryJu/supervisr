"""
Supervisr Invoke Tasks
"""
import os

from invoke import Collection

from supervisr._tasks import dev, supervisr

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supervisr.core.settings")
os.environ.setdefault("SUPERVISR_LOCAL_SETTINGS", "supervisr.local_settings")

# pylint: disable=invalid-name
namespace = Collection()
namespace.add_collection(Collection.from_module(supervisr))
namespace.add_collection(Collection.from_module(dev))
