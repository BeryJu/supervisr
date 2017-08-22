"""
Supervisr Bacula Apps Config
"""
import logging

from django.conf import settings

from supervisr.core.apps import SupervisrAppConfig

LOGGER = logging.getLogger(__name__)

class SupervisrModContribBaculaConfig(SupervisrAppConfig):
    """
    Supervisr Bacula app config
    """

    name = 'supervisr.mod.contrib.bacula'
    label = 'supervisr/mod/contrib/bacula'
    verbose_name = 'Supervisr Bacula'
    title_moddifier = lambda self, title, request: 'Bacula'

    def ready(self):
        super(SupervisrModContribBaculaConfig, self).ready()
        from supervisr.core.models import Setting
        if Setting.get('enabled') == 'True' and not settings.TEST:
            settings.DATABASES['bacula'] = {}
            for key in ['ENGINE', 'NAME', 'USER', 'PASSWORD', 'HOST']:
                settings.DATABASES['bacula'][key] = Setting.get(key.lower())

    def ensure_settings(self):
        return {
            'enabled': False,
            'engine': '',
            'name': '',
            'user': '',
            'password': '',
            'host': '',
            'port': '',
        }

    # pylint: disable=no-self-use
    def navbar_enabled(self, request):
        """
        Only show in navbar if enabled and superuser
        """
        from supervisr.core.models import Setting
        return request.user.is_superuser and Setting.get('enabled')
