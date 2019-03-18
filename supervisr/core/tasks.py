"""supervisr core tasks"""
import json
import time
from decimal import Decimal
from logging import getLogger

from celery import Task
from celery.result import AsyncResult
from django.conf import settings

from supervisr.core.celery import CELERY_APP
from supervisr.core.signals import StatisticType, on_set_statistic

LOGGER = getLogger(__name__)


# pylint: disable=too-few-public-methods
class BaseRecorder:
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

class SupervisrTask(Task):
    """Supervisr base task"""

    _invoker = None
    _progress = None

    def prepare(self, **kwargs):
        """Prepare this task, load invoker andadd some utilities"""
        from django.contrib.auth.models import User
        # Get Invoker if possible
        if 'invoker' in kwargs:
            users = User.objects.filter(pk=kwargs.get('invoker'))
            if users.exists():
                self._invoker = users.first()
        # Create a ProgressRecorder
        self._progress = ProgressRecorder(self)

    def run(self, *args, **kwargs):
        raise NotImplementedError()

    @property
    def invoker(self) -> 'User':
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
class Progress:
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
        if self.result.state == Progress.STATE_PROGRESS:
            return {
                'complete': False,
                'success': None,
                'progress': self.result.info,
            }
        if self.result.state in [Progress.STATE_PENDING, Progress.STATE_STARTED]:
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


class StatisticTask(SupervisrTask):
    """Task to save statistics. Also handles increasing and saving counter state"""

    name = 'supervisr.core.tasks.StatisticTask'
    __counters = None
    __path = ''

    # Count changes since last save
    __changes = 0
    # Time when last file was written
    __last_save = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__counters = {}
        self.__path = settings.DATA_DIR + '/cache/counters.json'
        self.__changes = 0
        self.__last_save = 0
        with open(self.__path, mode='a+') as _file:
            try:
                LOGGER.debug('Loaded counters.json')
                self.__counters = json.loads(_file.read())
            except json.decoder.JSONDecodeError:
                LOGGER.debug('failed to load json, resetting')
                self.__counters = {}

    def save(self):
        """Save counters to json file"""
        now = time.time()
        diff = now - self.__last_save
        # Write file to disk if more than 30 changes or more than 600 ms passed
        if self.__changes > 30 or diff > 600:
            with open(self.__path, 'w') as _file:
                self.__last_save = time.time()
                self.__changes = 0
                json.dump(self.__counters, _file)
                LOGGER.debug("wrote counters.json file")

    def run(self, name, values: dict, hints=None):
        """[summary]

        Args:
            name (str): Name of statistic
            values (dict): Dictionary of values. Structure:
                           {'value_name': {'value': <value>, 'type': StatisticType }}
            hints (dict, optional): Defaults to None. Optional dict of hints like units

        Raises:
            ValueError: [description]
        """
        # We differentiate between values based on statistic name and value name
        if name not in self.__counters:
            self.__counters[name] = {}
        flat_values = {}
        for value_name, value_body in values.items():
            # Flatten values while iterating
            flat_values[value_name] = value_body.get('value')
            # Signal is called on worker
            if value_body.get('type') == StatisticType.Counter:
                # Check if value is a digit, if not raise an Error
                if not str(value_body.get('value')).isdigit():
                    raise ValueError("Value needs to be numerical if Type is set to Counter.")
                if value_name not in self.__counters[name]:
                    # Initialize in-memory counters with current values
                    self.__counters[name][value_name] = value_body.get('value')
                else:
                    self.__counters[name][value_name] += value_body.get('value')
                    flat_values[value_name] = self.__counters[name][value_name]
                self.__changes += 1
        on_set_statistic.send(name=name, values=flat_values, hints=hints, sender=self)
        self.save()


CELERY_APP.tasks.register(StatisticTask())

@CELERY_APP.task(bind=True, base=SupervisrTask)
def debug_progress_task(self, seconds, **kwargs):
    """Debug task to test progress"""
    self.prepare(**kwargs)
    self.progress.total = seconds
    for i in range(seconds):
        time.sleep(1)
        self.progress.set(i + 1)
    return 'done'
