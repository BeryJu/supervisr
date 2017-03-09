#!/usr/bin/python3
"""
Supervisr Invoke Tasks
"""
try:
    from invoke import task
    from invoke.platform import WINDOWS
except ImportError:
     print("Could not import pyinvoke. Please install by running 'sudo pip3 install invoke'")

from glob import glob

if WINDOWS:
    PYTHON_EXEC = 'PYTHON_EXEC'
else:
    PYTHON_EXEC = 'PYTHON_EXEC3'

@task
def install(ctx, dev=False):
    """
    Install requirements for supervisr and all modules
    """
    files = glob("*/requirements.txt")
    if dev:
        files.extend(glob("*/requirements-dev.txt"))
    ctx.sudo("pip3 install -r %s" % ' -r '.join(files))

@task
def deploy(ctx, user=None, fqdn=None):
    """
    SSH into application server and update ourselves
    """
    ctx.run("ssh -o 'StrictHostKeyChecking=no' %s@%s \"./update_supervisr.sh\"" % (user, fqdn))

@task
def run_dev(ctx, port=8080):
    """
    Create & apply migrations and run a dev server on
    """
    ctx.run("%s manage.py makemigrations" % PYTHON_EXEC)
    ctx.run("%s manage.py migrate" % PYTHON_EXEC)
    ctx.run("%s manage.py runserver 0.0.0.0:%s" % (PYTHON_EXEC, port))
