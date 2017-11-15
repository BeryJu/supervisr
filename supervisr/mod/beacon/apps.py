"""
Supervisr module beacon app config
"""
from django.conf import settings

from supervisr.core.apps import SupervisrAppConfig
from supervisr.core.thread.background import SCHEDULER


class SupervisrModBeaconConfig(SupervisrAppConfig):
    """
    Supervisr module beacon app config
    """

    name = 'supervisr.mod.beacon'
    label = 'supervisr/mod/beacon'
    verbose_name = 'Supervisr mod/beacon'
    navbar_enabled = lambda self, request: True

    def ready(self):
        super(SupervisrModBeaconConfig, self).ready()
        if getattr(settings, 'BEACON_ENABLED', True):
            from supervisr.mod.beacon.sender import Sender
            sender = Sender()
            SCHEDULER.every(15).minutes.do(sender.tick)
            # Running a tick when the app starts breaks the admin interface somehow
            # since sender.tick calls reverse internally to figure out the endpoint URL.
            # sender.tick()
