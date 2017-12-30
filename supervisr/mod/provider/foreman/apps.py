"""
Supervisr module foreman app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModProviderForemanConfig(SupervisrAppConfig):
    """
    Supervisr module foreman app config
    """

    name = 'supervisr.mod.provider.foreman'
    init_modules = ['models', 'providers.core']
    label = 'supervisr/mod/provider/foreman'
    title_moddifier = lambda self, title, request: 'Provider/Foreman'
