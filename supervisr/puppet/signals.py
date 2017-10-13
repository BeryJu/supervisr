"""
Supervisr Puppet Signals
"""
import logging

from django.conf import settings
from django.dispatch import receiver

from supervisr.core.signals import SIG_DO_SETUP
from supervisr.puppet.utils import ForgeImporter

LOGGER = logging.getLogger(__name__)

@receiver(SIG_DO_SETUP)
# pylint: disable=unused-argument
def puppet_handle_do_setup(sender, signal, **kwargs):
    """
    Handle setup and import modules
    """
    if sender == 'supervisr.puppet' and not settings.TEST:
        for_imp = ForgeImporter()
        for_imp.import_module('puppetlabs-stdlib')
        LOGGER.info('Imported initial Dependencies')
