"""
Supervisr Web app config
"""

from supervisr.apps import SupervisrAppConfig


class SupervisrWebConfig(SupervisrAppConfig):
    """
    Supervisr Web app config
    """

    name = 'supervisr_web'
    verbose_name = 'Supervisr Web'

    def ready(self):
        super(SupervisrWebConfig, self).ready()
