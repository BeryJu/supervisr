"""supervisr core tasks"""
import time

from celery import Task

from supervisr.core.celery import CELERY_APP
from supervisr.core.models import User
from supervisr.core.progress import ProgressRecorder
from supervisr.core.signals import SIG_SET_STAT


class SupervisrTask(Task):
    """Supervisr base task"""

    _invoker = None
    _progress = None

    def prepare(self, **kwargs):
        """Prepare this task, load invoker andadd some utilities"""
        # Get Invoker if possible
        if 'invoker' in kwargs:
            users = User.objects.filter(pk=int(kwargs.get('invoker')))
            if users.exists():
                self._invoker = users.first()
        # Create a ProgressRecorder
        self._progress = ProgressRecorder(self)

    def run(self, *args, **kwargs):
        raise NotImplementedError()

    @property
    def invoker(self) -> User:
        """Get invoker if possible"""
        if self._invoker:
            return self._invoker
        return None

    @property
    def progress(self) -> ProgressRecorder:
        """Get ProgressRecorder"""
        if self._progress:
            return self._progress
        return None


@CELERY_APP.task(bind=True)
def stat_proxy(self, key, value):
    """Handle statistic sending in a task"""
    SIG_SET_STAT.send(key=key, value=value, sender=self)


@CELERY_APP.task(bind=True, base=SupervisrTask)
def debug_progress_task(self, seconds, **kwargs):
    """Debug task to test progress"""
    self.prepare(**kwargs)
    self.progress.total = seconds
    for i in range(seconds):
        time.sleep(1)
        self.progress.set(i + 1)
    return 'done'
