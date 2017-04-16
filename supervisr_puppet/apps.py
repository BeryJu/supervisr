"""
Supervisr Puppet Apps Config
"""

from supervisr.apps import SupervisrAppConfig


class SupervisrPuppetConfig(SupervisrAppConfig):
    """
    Supervisr Puppet app config
    """

    name = 'supervisr_puppet'
    verbose_name = 'Supervisr Puppet'

    def ready(self):
        super(SupervisrPuppetConfig, self).ready()
