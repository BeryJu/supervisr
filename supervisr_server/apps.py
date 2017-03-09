"""
Supervisr Server app config
"""

from supervisr.apps import SupervisrAppConfig


class SupervisrServerConfig(SupervisrAppConfig):
    """
    Supervisr Server app config
    """

    name = 'supervisr_server'
    verbose_name = 'Supervisr Server'

    def ready(self):
        super(SupervisrServerConfig, self).ready()
