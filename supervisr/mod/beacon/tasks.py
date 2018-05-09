"""supervisr mod beacon signals"""
from logging import getLogger

from supervisr.core.celery import CELERY_APP
from supervisr.core.decorators import time

LOGGER = getLogger(__name__)


@CELERY_APP.task(bind=True, hard_time_limit=30)
# pylint: disable=unused-argument
def run_sender(self):
    """Send data"""
    @time(statistic_key='mod_beacon_pulse')
    def send():
        """Wrap sending to a function so we can time it easier"""
        from supervisr.mod.beacon.sender import Sender
        sender = Sender()
        sender.tick()
        LOGGER.debug("Successfully sent beacon pulse.")
    send()
