"""Supervisr module Debug app config"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModProviderDebugConfig(SupervisrAppConfig):
    """Supervisr module Debug app config"""

    name = 'supervisr.mod.provider.debug'
    init_modules = ['models', 'providers.core']
    label = 'supervisr_mod_provider_debug'
    title_modifier = lambda self, request: 'Provider/Debug'
