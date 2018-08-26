"""supervisr core tasks"""
import time
from decimal import Decimal
from logging import getLogger

from celery import Task
from celery.result import AsyncResult

from supervisr.core.celery import CELERY_APP
from supervisr.core.models import User
from supervisr.core.signals import on_set_statistic

LOGGER = getLogger(__name__)

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
# pylint: disable=too-few-public-methods


class Progress(object):
    """Get progress from Task_ID"""

    STATE_PROGRESS = 'PROGRESS'
    STATE_PENDING = 'PENDING'
    STATE_STARTED = 'STARTED'

    def __init__(self, task_id):
        self.task_id = task_id
        self.result = AsyncResult(task_id)

    def get_info(self) -> dict:
        """Get task completion status"""
        if self.result.ready():
            return {
                'complete': True,
                'success': self.result.successful(),
                'progress': {
                    'current': 100,
                    'total': 100,
                    'percent': 100,
                }
            }
        elif self.result.state == Progress.STATE_PROGRESS:
            return {
                'complete': False,
                'success': None,
                'progress': self.result.info,
            }
        elif self.result.state in [Progress.STATE_PENDING, Progress.STATE_STARTED]:
            return {
                'complete': False,
                'success': None,
                'progress': {
                    'current': 0,
                    'total': 100,
                    'percent': 0,
                },
            }
        return self.result.info


# pylint: disable=too-few-public-methods
class BaseRecorder(object):
    """Base ProgressRecorder. Does nothing."""

    total = 100

    def set(self, current, total=None):
        """Handle progress change"""
        raise NotImplementedError()


# pylint: disable=too-few-public-methods
class LoggerProgressRecorder(BaseRecorder):
    """Logger ProgressRecorder. Outputs progress to logger."""

    def set(self, current, total=None):
        if total:
            self.total = total
        LOGGER.info('processed %s items of %s', current, total)
        print('processed {} items of {}'.format(current, total))


# pylint: disable=too-few-public-methods
class ProgressRecorder(BaseRecorder):
    """ProgressRecorder which calculates a decimal percentage."""

    def __init__(self, task):
        self.task = task

    def set(self, current, total=None):
        if total:
            self.total = total
        if self.total == 0:
            percent = 0
        percent = round((Decimal(current) / Decimal(self.total)) * Decimal(100), 2)
        self.task.update_state(
            state=Progress.STATE_PROGRESS,
            meta={
                'current': current,
                'total': total,
                'percent': percent,
            }
        )


@CELERY_APP.task(bind=True)
def stat_proxy(self, key, value):
    """Handle statistic sending in a task"""
    on_set_statistic.send(key=key, value=value, sender=self)


@CELERY_APP.task(bind=True, base=SupervisrTask)
def debug_progress_task(self, seconds, **kwargs):
    """Debug task to test progress"""
    self.prepare(**kwargs)
    self.progress.total = seconds
    for i in range(seconds):
        time.sleep(1)
        self.progress.set(i + 1)
    return 'done'
