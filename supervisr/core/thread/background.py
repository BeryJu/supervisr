"""
Supervisr Core Thread BackgroundThread
"""
import logging
import time
from threading import Thread

from django.dispatch import Signal
from schedule import Scheduler

LOGGER = logging.getLogger(__name__)


class BackgroundThread(Thread):
    """
    Supervisr Thread to run background tasks
    """

    def __init__(self):
        super(BackgroundThread, self).__init__()
        self.schedule = Scheduler()
        self.daemon = True
        self.name = 'Supervisr Background Thread'
        SIG_GET_SCHEDULER.send(sender=self, scheduler=self.schedule)

    def run(self):
        """
        Run Scheduler
        """
        while True:
            self.schedule.run_pending()
            time.sleep(1)

SIG_GET_SCHEDULER = Signal(providing_args=['scheduler'])
