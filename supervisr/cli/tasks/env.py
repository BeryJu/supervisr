"""Supervisr Invoke CI tasks"""
import logging
import os

import pymysql
from invoke import task

LOGGER = logging.getLogger(__name__)
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
    from django.core.management import execute_from_command_line
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
