"""supervisr core celery"""

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supervisr.core.settings")
os.environ.setdefault("SUPERVISR_LOCAL_SETTINGS", "supervisr.local_settings")

CELERY_APP = Celery('supervisr')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
CELERY_APP.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
CELERY_APP.autodiscover_tasks()
