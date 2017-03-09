"""
Supervisr Mail app config
"""

from supervisr.apps import SupervisrAppConfig


class SupervisrMailConfig(SupervisrAppConfig):
    """
    Supervisr Mail app config
    """

    name = 'supervisr_mail'
    verbose_name = 'Supervisr Mail'

    def ready(self):
        super(SupervisrMailConfig, self).ready()
