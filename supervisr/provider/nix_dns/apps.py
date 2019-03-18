"""Supervisr module NixDNS app config"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModProviderNixDNSConfig(SupervisrAppConfig):
    """Supervisr module NixDNS app config"""

    name = 'supervisr.provider.nix_dns'
    init_modules = ['models', 'providers.core']
    label = 'supervisr_provider_nix_dns'
    title_modifier = lambda self, request: 'Provider/*nix DNS'
