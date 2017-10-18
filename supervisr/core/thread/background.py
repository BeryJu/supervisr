"""
Supervisr Core Thread BackgroundThread
"""
import logging
import time
import traceback
from threading import Thread
from typing import Callable

from schedule import CancelJob, Scheduler

LOGGER = logging.getLogger(__name__)
SCHEDULER = Scheduler()


def catch_exceptions(cancel_on_failure: bool = False) -> Callable:
    """Wrap a job to handle exceptions and cancel it on failure if cancel_on_failure is True

    Args:
        cancel_on_failure: If True, Job is canceled on Error. Defaults to False.

    Returns:
        Wrapper around function
    """
    def outer_wrap(job_func):
        """Outer wrapper"""
        def wrapper(*args, **kwargs):
            """Inner Wrapper"""
            try:
                return job_func(*args, **kwargs)
            # pylint: disable=bare-except
            except:
                LOGGER.warning(traceback.format_exc())
                if cancel_on_failure:
                    return CancelJob
        return wrapper

    return outer_wrap

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
