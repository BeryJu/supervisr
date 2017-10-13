"""
Supervisr Core Thread BackgroundThread
"""
import logging
import time
from threading import Thread

from schedule import Scheduler

LOGGER = logging.getLogger(__name__)
SCHEDULER = Scheduler()


class BackgroundThread(Thread):
    """
    Supervisr Thread to run background tasks
    """

    def __init__(self):
        super(BackgroundThread, self).__init__()
        self.daemon = True
        self.name = 'Supervisr Background Thread'

    def run(self):
        """
        Run Scheduler
        """
        while True:
            SCHEDULER.run_pending()
            time.sleep(1)
