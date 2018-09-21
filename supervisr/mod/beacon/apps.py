"""Supervisr module beacon app config"""

from supervisr.core.apps import SettingBootstrapper, SupervisrAppConfig


class SupervisrModBeaconConfig(SupervisrAppConfig):
    """Supervisr module beacon app config"""

    name = 'supervisr.mod.beacon'
    label = 'supervisr_mod_beacon'
    verbose_name = 'Supervisr mod_beacon'
    admin_url_name = 'supervisr_mod_beacon:admin_settings'
    title_modifier = lambda self, request: 'Beacon'
    navbar_enabled = lambda self, request: True

    def bootstrap(self):
        settings = SettingBootstrapper()
        settings.add(key='enabled', value=True)
        settings.add(key='endpoint', value='https://my.beryju.org')
        return settings,
