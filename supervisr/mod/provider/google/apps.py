"""
Supervisr module google app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModProviderGoogleConfig(SupervisrAppConfig):
    """
    Supervisr module google app config
    """

    name = 'supervisr.mod.provider.google'
    label = 'supervisr/mod/provider/google'
    title_modifier = lambda self, title, request: 'Provider/Google'
