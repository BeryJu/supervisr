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
import sys
from glob import glob

if WINDOWS:
    PYTHON_EXEC = 'python'
else:
    PYTHON_EXEC = 'python3'

def _sudo(ctx, *args, **kwargs):
    """
    Use .run if there's no tty (CI Build) or .sudo if there is one
    """
    if sys.stdout.isatty():
        return ctx.sudo(*args, **kwargs)
    else:
        return ctx.run(*args, **kwargs)

@task
def clean(ctx):
    """
    Clean Python cached files
    """
    files = glob("**/**/**/*.pyc", recursive=True)
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
    _sudo(ctx, "pip3 install -r %s" % ' -r '.join(files))

@task
def deploy(ctx, user=None, fqdn=None):
    """
    SSH into application server and update ourselves
    """
    ctx.run("ssh -o 'StrictHostKeyChecking=no' %s@%s \"./update_supervisr.sh\"" % (user, fqdn))

@task
def dj_make_migrations(ctx):
    """
    Create migrations
    """
    ctx.run("%s manage.py makemigrations" % PYTHON_EXEC)

@task(pre=[dj_make_migrations])
def dj_migrate(ctx):
    """
    Apply  migrations
    """
    ctx.run("%s manage.py migrate" % PYTHON_EXEC)

@task(pre=[dj_migrate])
def dj_run(ctx, port=8080):
    """
    Starts a development server
    """
    ctx.run("%s manage.py runserver 0.0.0.0:%s" % (PYTHON_EXEC, port))

@task
def lint(ctx):
    """
    Run PyLint
    """
    ctx.run("pylint --load-plugins pylint_django supervisr*")
