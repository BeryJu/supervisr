"""
Supervisr module apploader app config
"""
import logging
from collections import OrderedDict
from importlib import import_module
from threading import Thread
from time import sleep

from django.apps import apps
from django.conf import settings
from django.db.utils import InternalError, OperationalError, ProgrammingError

from supervisr.core.apps import SupervisrAppConfig
from supervisr.mod.apploader.utils import cls_path, find_apps, load_app

LOGGER = logging.getLogger(__name__)

class SupervisrModAppLoaderConfig(SupervisrAppConfig):
    """
    Supervisr module apploader app config
    """

    name = 'supervisr.mod.apploader'
    label = 'supervisr/mod/apploader'

    def ready(self):
        super(SupervisrModAppLoaderConfig, self).ready()
        all_apps = find_apps()
        try:
            self.update_db(all_apps)
            thread = Thread(target=load_apps_from_db)
            thread.start()
        except (InternalError, OperationalError, ProgrammingError):
            pass

    # pylint: disable=no-self-use
    def update_db(self, all_apps):
        """
        Import Apps from FS into DB
        """
        from supervisr.mod.apploader.models import DBApp
        for app in all_apps:
            DBApp.objects.get_or_create(
                path=cls_path(app),
                defaults={
                    'name': app.name,
                    'enabled': True,
                })


def load_apps_from_db():
    """
    Load apps from DB
    """
    sleep(10)
    from supervisr.mod.apploader.models import DBApp
    if getattr(settings, '__AUTO_DONE__', True):
        for dba in DBApp.objects.filter(enabled=True):
            try:
                path_parts = dba.path.split('.')
                module = import_module('.'.join(path_parts[:-1]))
                _class = getattr(module, path_parts[-1])
                load_app(dba.path, _class)
            except ImportError as exc:
                LOGGER.info("App %s failed to load: %s", dba.path, exc)
        settings.__AUTO_DONE__ = False
        apps.app_configs = OrderedDict()
        # set ready to false so that populate will work
        apps.ready = False
        apps.populate(settings.INSTALLED_APPS) # pylint: disable=no-member
        print(settings.INSTALLED_APPS)
