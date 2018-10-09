"""Supervisr Invoke CI tasks"""
import inspect
import os
import os.path
from logging import getLogger

import pymysql
from django import setup
from django.core.management import execute_from_command_line
from invoke import task

LOGGER = getLogger(__name__)
pymysql.install_as_MySQLdb()


@task
# pylint: disable=unused-argument
def lint(ctx, modules=None):
    """Run PyLint"""
    if modules is None:
        modules = ['tasks.py', 'supervisr']
    elif isinstance(modules, str):
        modules = [modules]

    from pylint.lint import Run
    Run(modules)

@task
def lint_ui(context):
    """Run TSLint"""
    from django.conf import settings
    with context.cd(settings.BASE_DIR + '/ui'):
        context.run('npx tslint -c tslint.json --project src')

@task
# pylint: disable=unused-argument
def pyroma(ctx):
    """Check setup.py"""
    from pyroma import run
    run('directory', '.')


@task
def prospector(ctx):
    """Run prospector"""
    ctx.run("prospector")


@task
def isort(ctx):
    """Run isort"""
    ctx.run("isort -c -sg env")


@task()
def coverage(ctx, module='supervisr', post_action='report'):
    """Run Unittests and get coverage"""
    ctx.run("coverage run --source=%s sv manage test" % module)
    ctx.run("coverage %s" % post_action)


@task
# pylint: disable=unused-argument
def test(ctx):
    """Run Unittests"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supervisr.core.settings")
    os.environ.setdefault("SUPERVISR_ENV", "local")
    execute_from_command_line(['', 'test'])


@task(pre=[isort, coverage, lint, prospector, test])
# Some tasks to make full testing easier
# pylint: disable=unused-argument
def test_complete(ctx):
    """Run all tests"""
    pass


@task
def docs(ctx):
    """Build pdoc docs"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supervisr.core.settings')
    os.makedirs('docgen', exist_ok=True)
    ctx.run("pdoc supervisr --html --html-dir=\"docgen\""
            " --django  --overwrite --docstring-style=google")


@task
# pylint: disable=unused-argument
def makemessages(ctx, locale='en'):
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
