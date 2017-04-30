"""
Supervisr module namecheap app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModNamecheapConfig(SupervisrAppConfig):
    """
    Supervisr module namecheap app config
    """

    name = 'supervisr.mod.namecheap'
    init_modules = ['signals', 'events', 'models', 'providers.core', 'providers.domain']
