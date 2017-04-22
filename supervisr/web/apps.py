"""
Supervisr Web app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrWebConfig(SupervisrAppConfig):
    """
    Supervisr Web app config
    """

    name = 'supervisr.web'
    verbose_name = 'Supervisr Web'

    def ready(self):
        super(SupervisrWebConfig, self).ready()
