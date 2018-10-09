"""supervisr dev tasks"""
from logging import getLogger

from django.core.management import execute_from_command_line
from invoke import task

LOGGER = getLogger(__name__)


@task
# pylint: disable=unused-argument
def init(ctx, name):
    """Create a new supervisr module"""
    execute_from_command_line(['', 'startapp', '--template', 'supervisr/cli/seed', name])
    LOGGER.info("Started Django App")
