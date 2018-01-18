"""Supervisr module beacon app config"""

from supervisr.core.apps import SupervisrAppConfig
from supervisr.core.thread.background import SCHEDULER


class SupervisrModBeaconConfig(SupervisrAppConfig):
    """Supervisr module beacon app config"""

    name = 'supervisr.mod.beacon'
    label = 'supervisr_mod_beacon'
    verbose_name = 'Supervisr mod_beacon'
    admin_url_name = 'supervisr_mod_beacon:admin_settings'
    title_modifier = lambda self, request: 'Beacon'
    navbar_enabled = lambda self, request: True

    def ready(self):
        super(SupervisrModBeaconConfig, self).ready()
        from supervisr.mod.beacon.sender import Sender
        sender = Sender()
        SCHEDULER.every(15).minutes.do(sender.tick)
        # Running a tick when the app starts breaks the admin interface somehow
        # since sender.tick calls reverse internally to figure out the endpoint URL.
        # sender.tick()

    def ensure_settings(self):
        return {
            'enabled': True,
            'endpoint': 'https://my.beryju.org'
        }
