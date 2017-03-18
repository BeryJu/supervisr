#!/usr/bin/python3
"""
Supervisr Invoke Tasks
"""
try:
    from invoke import task
    from invoke.platform import WINDOWS
except ImportError:
    print("Could not import pyinvoke. Please install by running 'sudo pip3 install invoke'")

import os
import shutil
from functools import wraps
from glob import glob

if WINDOWS:
    PYTHON_EXEC = 'python'
else:
    PYTHON_EXEC = 'python3'

def shell(func):
    """
    Fixes the Shell on Windows Systems
    """
    @wraps(func)
    def wrapped(ctx, *args, **kwargs):
        """
        Fixes the Shell on Windows Systems
        """
        if WINDOWS:
            ctx.config.run.shell = "C:\\Windows\\System32\\cmd.exe"
        return func(ctx, *args, **kwargs)
    return wrapped

def hide(func):
    """
    Hides the STDOUT of ctx.run
    """
    @wraps(func)
    def wrapped(ctx, *args, **kwargs):
        """
        Hides the STDOUT of ctx.run
        """
        ctx.config.run.hide = 'stdout'
        ret = func(ctx, *args, **kwargs)
        return ret
    return wrapped

@task
# pylint: disable=unused-argument
def clean(ctx):
    """
    Clean Python cached files
    """
    files = glob("**/**/**/*.pyc")
    for file in files:
        os.remove(file)
    print("Removed %i files" % len(files))

@task
def install(ctx, dev=False):
    """
    Install requirements for supervisr and all modules
    """
    files = glob("*/requirements.txt")
    if dev:
        files.extend(glob("*/requirements-dev.txt"))
    ctx.run("pip3 install -r %s" % ' -r '.join(files))

@task
def deploy(ctx, user=None, fqdn=None):
    """
    SSH into application server and update ourselves
    """
    ctx.run("ssh -o 'StrictHostKeyChecking=no' %s@%s \"./update_supervisr.sh\"" % (user, fqdn))

@task
@shell
def make_migrations(ctx):
    """
    Create migrations
    """
    ctx.run("%s manage.py makemigrations" % PYTHON_EXEC)

@task(pre=[make_migrations])
@shell
@hide
def migrate(ctx):
    """
    Apply migrations
    """
    ctx.run("%s manage.py migrate" % PYTHON_EXEC)

@task(pre=[migrate])
@shell
def run(ctx, port=8080):
    """
    Starts a development server
    """
    ctx.run("%s manage.py runserver 0.0.0.0:%s" % (PYTHON_EXEC, port))

@task
# pylint: disable=unused-argument
def lint(ctx, modules=None):
    """
    Run PyLint
    """
    if modules is None:
        modules = ['tasks.py']
        modules.extend(glob('supervisr*'))
    elif isinstance(modules, str):
        modules = [modules]

    from pylint.lint import Run
    args = ['--load-plugins', 'pylint_django']
    args.extend(modules)
    Run(args)

@task
@shell
def prospector(ctx):
    """
    Run prospector
    """
    ctx.run("prospector -I migration")

@task
@shell
@hide
def isort(ctx):
    """
    Run isort
    """
    ctx.run("isort -c -vb")

@task(pre=[migrate])
@shell
def coverage(ctx):
    """
    Run Unittests and get coverage
    """
    ctx.run("coverage run --source='.' manage.py test --pattern=Test*.py")
    ctx.run("coverage report")

@task
@shell
@hide
def unittest(ctx):
    """
    Run Unittests
    """
    ctx.run("%s manage.py test --pattern=Test*.py" % PYTHON_EXEC)

# Some tasks to make full testing easier
@task(pre=[migrate, unittest, coverage, isort, lint, prospector])
# pylint: disable=unused-argument
def test(ctx):
    """
    Run all tests
    """
    pass

@task
@shell
def docs(ctx):
    """
    Build sphinx docs
    """
    shutil.rmtree('docs/build', ignore_errors=True)
    ctx.run('sphinx-apidoc -o docs/source '+' '.join(glob('supervisr*')))
    ctx.run('sphinx-build -b html docs/source docs/build')
