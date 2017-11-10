"""
Supervisr Mail app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrMailConfig(SupervisrAppConfig):
    """
    Supervisr Mail app config
    """

    name = 'supervisr.mail'
    label = 'supervisr/mail'
    verbose_name = 'Supervisr Mail'
    navbar_enabled = lambda self, request: True
    title_modifier = lambda self, title, request: 'Mail'

    def ensure_settings(self):
        return {
            'debug': False,
        }
