"""
Supervisr module namecheap app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModProviderNamecheapConfig(SupervisrAppConfig):
    """
    Supervisr module namecheap app config
    """

    name = 'supervisr.mod.provider.namecheap'
    init_modules = ['models', 'providers.core', 'providers.domain']
    label = 'supervisr/mod/provider/namecheap'
