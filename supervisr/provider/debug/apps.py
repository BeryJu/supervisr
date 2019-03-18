"""Supervisr module Debug app config"""

from supervisr.core.apps import SettingBootstrapper, SupervisrAppConfig


class SupervisrModProviderDebugConfig(SupervisrAppConfig):
    """Supervisr module Debug app config"""

    name = 'supervisr.provider.debug'
    init_modules = ['providers.core']
    label = 'supervisr_provider_debug'
    title_modifier = lambda self, request: 'Provider/Debug'

    def bootstrap(self):
        """Add permissions and settings"""
        settings = SettingBootstrapper()
        settings.add(key='sleep_duration', value=10)
        return (settings, )
