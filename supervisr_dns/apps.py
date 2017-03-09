"""
Supervisr DNS app config
"""

from supervisr.apps import SupervisrAppConfig


class SupervisrDNSConfig(SupervisrAppConfig):
    """
    Supervisr DNS app config
    """

    name = 'supervisr_dns'
    verbose_name = 'Supervisr DNS'

    def ready(self):
        super(SupervisrDNSConfig, self).ready()
