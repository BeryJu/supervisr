"""
Supervisr DNS app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrDNSConfig(SupervisrAppConfig):
    """
    Supervisr DNS app config
    """

    name = 'supervisr.dns'
    verbose_name = 'Supervisr DNS'
    navbar_title = 'DNS'

    def ready(self):
        super(SupervisrDNSConfig, self).ready()
