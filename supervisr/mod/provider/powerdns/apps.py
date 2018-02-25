"""Supervisr module PowerDNS app config"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModProviderPowerDNSConfig(SupervisrAppConfig):
    """Supervisr module PowerDNS app config"""

    name = 'supervisr.mod.provider.powerdns'
    init_modules = ['models', 'providers.core']
    label = 'supervisr_mod_provider_powerdns'
    title_modifier = lambda self, request: 'Provider/PowerDNS'
