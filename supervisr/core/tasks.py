"""supervisr core tasks"""

from supervisr.core.celery import CELERY_APP
from supervisr.core.signals import SIG_SET_STAT


@CELERY_APP.task(bind=True)
def stat_proxy(self, key, value):
    """Handle statistic sending in a task"""
    SIG_SET_STAT.send(key=key, value=value, sender=self)
