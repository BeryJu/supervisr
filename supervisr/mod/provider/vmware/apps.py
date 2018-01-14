"""Supervisr module provider vmware app config"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModProviderVMwareConfig(SupervisrAppConfig):
    """Supervisr module provider vmware app config"""

    name = 'supervisr.mod.provider.vmware'
    init_modules = ['providers.core']
    label = 'supervisr_mod_provider_vmware'
