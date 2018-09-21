"""Supervisr Core celery worker ManagementCommand"""
import logging
import shlex
import subprocess  # nosec

from django.core.management.base import BaseCommand
from django.utils import autoreload

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """Run celery worker with auto-reload"""

    help = 'Run celery worker with auto-reload'

    KILL_COMMAND = 'pkill -f "python manage.py celery_debug"'
    START_COMMAND = 'celery -A supervisr.core worker -l debug -Ofair -E'

    def handle(self, *args, **options):
        LOGGER.debug('Starting celery worker with autoreload...')

        def restart_celery():
            """Starter function"""
            subprocess.call(shlex.split(self.KILL_COMMAND)) # nosec
            subprocess.call(shlex.split(self.START_COMMAND)) # nosec
        autoreload.main(restart_celery)
