"""Supervisr Invoke CI tasks"""
import logging
import os
from functools import wraps

from invoke import task
from invoke.terminals import WINDOWS

if WINDOWS:
    PYTHON_EXEC = 'python'
else:
    PYTHON_EXEC = 'python3'
LOGGER = logging.getLogger(__name__)


def shell(func):
    """Fixes the Shell on Windows Systems"""
    @wraps(func)
    def wrapped(ctx, *args, **kwargs):
        """Fixes the Shell on Windows Systems"""
        if WINDOWS:
            ctx.config.run.shell = "C:\\Windows\\System32\\cmd.exe"
        return func(ctx, *args, **kwargs)
    return wrapped


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
# pylint: disable=unused-argument
def pyroma(ctx):
    """Check setup.py"""
    from pyroma import run
    run('directory', '.')


@task
@shell
def prospector(ctx):
    """Run prospector"""
    ctx.run("prospector")


@task
@shell
def isort(ctx):
    """Run isort"""
    ctx.run("isort -c -sg env")


@task()
def coverage(ctx, module='supervisr', post_action='report'):
    """Run Unittests and get coverage"""
    if WINDOWS:
        ctx.config.run.shell = "C:\\Windows\\System32\\cmd.exe"
    ctx.run("coverage run --source=%s manage.py test" % module)
    ctx.run("coverage %s" % post_action)


@task
@shell
def unittest(ctx):
    """Run Unittests"""
    ctx.run("%s manage.py test" % PYTHON_EXEC)


@task(pre=[isort, coverage, lint, prospector])
# Some tasks to make full testing easier
# pylint: disable=unused-argument
def test(ctx):
    """Run all tests"""
    pass


@task
@shell
def docs(ctx):
    """Build pdoc docs"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supervisr.core.settings')
    tool = 'pdoc'
    if WINDOWS:
        tool = 'python env\\Scripts\\pdoc'
    os.makedirs('docgen')
    ctx.run("%s supervisr --html --html-dir=\"docgen\""
            " --html-no-source  --overwrite --docstring-style=google" % tool)
