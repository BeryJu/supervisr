"""supervisr mod beacon signals"""
from celery.schedules import crontab
from django.dispatch import receiver

from supervisr.core.celery import CELERY_APP
from supervisr.core.signals import SIG_CELERY_SCHEDULER


@receiver(SIG_CELERY_SCHEDULER)
# pylint: disable=unused-argument
def start_beacon_schedule(sender, *args, **kwargs):
    """Start beacon sender schedule"""
    from supervisr.mod.beacon.sender import Sender
    beacon_sender = Sender()
    sender.add_periodic_task(
        crontab(minute='*/15'),
        run_sender.s(beacon_sender)
    )
    # Running a tick when the app starts breaks the admin interface somehow
    # since sender.tick calls reverse internally to figure out the endpoint URL.
    # sender.tick()


@CELERY_APP.task(bind=True)
# pylint: disable=unused-argument
def run_sender(self, sender):
    """Send data"""
    sender.tick()
