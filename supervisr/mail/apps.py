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
    navbar_enabled = lambda self, request: True

    def ensure_settings(self):
        return {
            'mail:debug': False,
        }
