"""Supervisr module google app config"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModProviderGoogleConfig(SupervisrAppConfig):
    """Supervisr module google app config"""

    name = 'supervisr.mod.provider.google'
    label = 'supervisr_mod_provider_google'
    title_modifier = lambda self, request: 'Provider/Google'
