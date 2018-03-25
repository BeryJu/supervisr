"""supervisr apache libcloud provider"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModProviderLibcloud(SupervisrAppConfig):
    """supervisr apache libcloud provider"""

    name = 'supervisr.mod.provider.libcloud'
    init_modules = ['models', 'providers.core']
    label = 'supervisr_mod_provider_libcloud'
    title_modifier = lambda self, request: 'Provider/libcloud'
