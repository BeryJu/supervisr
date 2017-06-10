"""
Supervisr Puppet Apps Config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrPuppetConfig(SupervisrAppConfig):
    """
    Supervisr Puppet app config
    """

    name = 'supervisr.puppet'
    verbose_name = 'Supervisr Puppet'
