"""
Supervisr Mail app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrMailConfig(SupervisrAppConfig):
    """
    Supervisr Mail app config
    """

    name = 'supervisr.mail'
    verbose_name = 'Supervisr Mail'

    def ready(self):
        super(SupervisrMailConfig, self).ready()
