"""
Supervisr Puppet Apps Config
"""

import logging

from django.db.utils import OperationalError

from supervisr.core.apps import SupervisrAppConfig

LOGGER = logging.getLogger(__name__)

class SupervisrPuppetConfig(SupervisrAppConfig):
    """
    Supervisr Puppet app config
    """

    name = 'supervisr.puppet'
    verbose_name = 'Supervisr Puppet'

    def ready(self):
        super(SupervisrPuppetConfig, self).ready()
        # self.initial_import()

    @staticmethod
    def initial_import():
        """
        Import always needed puppet libs
        """
        try:
            from supervisr.puppet.utils import ForgeImporter
            for_imp = ForgeImporter()
            for_imp.import_module('puppetlabs-stdlib')
            LOGGER.info('Imported initial Dependencies')
        except OperationalError:
            pass
