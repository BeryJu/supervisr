"""supervisr core celery"""

import logging
import os

import celery
import pymysql
from django.conf import settings
from raven import Client
from raven.contrib.celery import register_logger_signal, register_signal

pymysql.install_as_MySQLdb()

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supervisr.core.settings")
os.environ.setdefault("SUPERVISR_LOCAL_SETTINGS", "supervisr.local_settings")

LOGGER = logging.getLogger(__name__)

class Celery(celery.Celery):
    """Custom Celery class with Raven configured"""

    # pylint: disable=method-hidden
    def on_configure(self):
        """Update raven client"""
        client = Client(settings.SENTRY_DSN)
        # register a custom filter to filter out duplicate logs
        register_logger_signal(client)
        # hook into the Celery error handler
        register_signal(client)


# pylint: disable=unused-argument
@celery.signals.setup_logging.connect
def config_loggers(*args, **kwags):
    """Apply logging settings from settings.py to celery"""
    logging.config.dictConfig(settings.LOGGING)


# pylint: disable=unused-argument
@celery.signals.after_task_publish.connect
def after_task_publish_handler(sender=None, headers=None, body=None, **kwargs):
    """Log task_id after it was published"""
    info = headers if 'task' in headers else body
    LOGGER.debug('for task id %s', info.get('id'))


# pylint: disable=unused-argument
@celery.signals.task_prerun.connect
def task_prerun_handler(task_id, task, *args, **kwargs):
    """Log task_id on worker"""
    LOGGER.debug('for task id %s', task_id)


# pylint: disable=unused-argument
@celery.signals.task_postrun.connect
def task_postrun_handler(task_id, task, *args, retval=None, state=None, **kwargs):
    """Log task_id on worker"""
    LOGGER.debug('for task id %s (state=%s)', task_id, state)


CELERY_APP = Celery('supervisr')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
CELERY_APP.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
CELERY_APP.autodiscover_tasks()
