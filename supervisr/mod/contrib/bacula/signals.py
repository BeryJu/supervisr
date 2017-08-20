"""
Supervisr Contrib Bacula signals
"""

from django.conf import settings
from django.dispatch import receiver

from supervisr.core.models import Setting
from supervisr.core.signals import SIG_SETTING_UPDATE


@receiver(SIG_SETTING_UPDATE)
# pylint: disable=unused-argument
def update_bacula_db(sender, **kwargs):
    """
    Update Bacula DB from settings
    """
    if sender.namespace == 'supervisr.mod.contrib.bacula':
        if Setting.get('enabled'):
            settings.DATABASES['bacula'] = {}
            for key in ['ENGINE', 'NAME', 'USER', 'PASSWORD', 'HOST']:
                settings.DATABASES['bacula'][key] = Setting.get(key.lower())
