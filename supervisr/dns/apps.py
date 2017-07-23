"""
Supervisr DNS app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrDNSConfig(SupervisrAppConfig):
    """
    Supervisr DNS app config
    """

    name = 'supervisr.dns'
    label = 'supervisr/dns'
    verbose_name = 'Supervisr DNS'
    navbar_enabled = lambda self, request: True
    title_moddifier = lambda self, title, request: 'dns'.upper()
