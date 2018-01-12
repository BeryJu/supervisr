"""Supervisr Bacula Apps Config"""
import logging

from django.conf import settings

from supervisr.core.apps import SupervisrAppConfig

LOGGER = logging.getLogger(__name__)

class SupervisrModContribBaculaConfig(SupervisrAppConfig):
    """Supervisr Bacula app config"""

    name = 'supervisr.mod.contrib.bacula'
    label = 'supervisr_mod_contrib_bacula'
    verbose_name = 'Supervisr mod_contrib_bacula'
    title_modifier = lambda self, request: 'Bacula'
    admin_url_name = 'supervisr_mod_contrib_bacula:settings'

    def ready(self):
        super(SupervisrModContribBaculaConfig, self).ready()
        from supervisr.core.models import Setting
        if Setting.get_bool('enabled') and not settings.TEST:
            settings.DATABASES['bacula'] = {}
            for key in ['ENGINE', 'NAME', 'USER', 'PASSWORD', 'HOST']:
                settings.DATABASES['bacula'][key] = Setting.get(key.lower())
            # Manually set strict mode if mysql
            if 'mysql' in settings.DATABASES['bacula']['ENGINE']:
                settings.DATABASES['bacula']['OPTIONS'] = {
                    'init_command': """
                    SET sql_mode='STRICT_TRANS_TABLES';
                    """
                }

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
    def navbar_enabled(self, req):
        """
        Only show in navbar if enabled and superuser
        """
        from supervisr.core.models import Setting
        return req.user.is_superuser and Setting.get_bool('enabled')
