"""Supervisr module beacon app config"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModBeaconConfig(SupervisrAppConfig):
    """Supervisr module beacon app config"""

    name = 'supervisr.mod.beacon'
    label = 'supervisr_mod_beacon'
    verbose_name = 'Supervisr mod_beacon'
    admin_url_name = 'supervisr_mod_beacon:admin_settings'
    title_modifier = lambda self, request: 'Beacon'
    navbar_enabled = lambda self, request: True

    def ensure_settings(self):
        return {
            'enabled': True,
            'endpoint': 'https://my.beryju.org'
        }
