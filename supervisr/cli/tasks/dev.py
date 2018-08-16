"""supervisr dev tasks"""
import inspect
import logging
import os
import os.path

from django import setup
from django.core.management import execute_from_command_line
from invoke import task

LOGGER = logging.getLogger(__name__)


@task
# pylint: disable=unused-argument
def init(ctx, name):
    """Create a new supervisr module"""
    execute_from_command_line(['', 'startapp', name])
    LOGGER.info("Started Django App")

@task
# pylint: disable=unused-argument
def makemessages(ctx, locale=''):
    """Create .po files for every supervisr app"""
    setup()
    from django.core.management.commands.makemessages import Command
    from supervisr.core.utils import get_apps, LogOutputWrapper
    # Returns list of app starting with supervisr
    for app in get_apps(exclude=[]):
        # Get apps.py file from class
        app_file = inspect.getfile(app.__class__)
        # Get app basedir and change to it
        app_basedir = os.path.dirname(app_file)
        os.chdir(app_basedir)
        # Create locale dir in case it doesnt exist
        os.makedirs('locale', exist_ok=True)
        LOGGER.info("Building %s", app.__class__.__name__)
        builder = Command(stdout=LogOutputWrapper())
        builder.handle(
            verbosity=1,
            settings=None,
            pythonpath=None,
            traceback=None,
            no_color=False,
            locale=locale.split(','),
            exclude=[],
            domain='django',
            all=False,
            extensions=None,
            symlinks=False,
            ignore_patterns=[],
            use_default_ignore_patterns=True,
            no_wrap=False,
            no_location=False,
            add_location=None,
            no_obsolete=False,
            keep_pot=False,
        )
