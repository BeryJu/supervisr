#!/usr/bin/which python3
"""
Supervisr Invoke Tasks
"""
from invoke import task
from invoke.platform import WINDOWS

if WINDOWS:
    PYTHON_EXEC = 'PYTHON_EXEC'
else:
    PYTHON_EXEC = 'PYTHON_EXEC3'

@task
def clean(ctx):
    patterns = ['build']
    for pattern in patterns:
        ctx.run("rm -rf %s" % pattern)

@task
def deploy(ctx, user=None, fqdn=None):
    """
    SSH into application server and update ourselves
    """
    ctx.run("ssh -o 'StrictHostKeyChecking=no' %s@%s \"./update_supervisr.sh\"" % (user, fqdn))

@task
def run_dev(ctx, port=8080):
    ctx.run("%s manage.py makemigrations" % PYTHON_EXEC)
    ctx.run("%s manage.py migrate" % PYTHON_EXEC)
    ctx.run("%s manage.py runserver 0.0.0.0:%s" % (PYTHON_EXEC, port))

@task
def build(ctx, docs=False):
    ctx.run("PYTHON_EXEC setup.py build")
    if docs:
        ctx.run("sphinx-build docs docs/_build")
