"""
Supervisr Puppet Apps Config
"""

import logging

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
