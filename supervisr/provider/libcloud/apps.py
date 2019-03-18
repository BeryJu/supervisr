"""supervisr apache libcloud provider"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModProviderLibcloud(SupervisrAppConfig):
    """supervisr apache libcloud provider"""

    name = 'supervisr.provider.libcloud'
    init_modules = ['models', 'providers.core']
    label = 'supervisr_provider_libcloud'
    title_modifier = lambda self, request: 'Provider/libcloud'
