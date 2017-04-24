"""
Supervisr Server app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrServerConfig(SupervisrAppConfig):
    """
    Supervisr Server app config
    """

    name = 'supervisr.server'
    verbose_name = 'Supervisr Server'

    def ready(self):
        super(SupervisrServerConfig, self).ready()
