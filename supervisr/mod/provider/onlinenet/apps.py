"""
Supervisr module online.net app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModProviderOnlineNetConfig(SupervisrAppConfig):
    """
    Supervisr module online.net app config
    """

    name = 'supervisr.mod.provider.onlinenet'
    init_modules = ['models', 'providers.core']
    label = 'supervisr/mod/provider/onlinenet'
    title_modifier = lambda self, title, request: 'Provider/Online.net'
