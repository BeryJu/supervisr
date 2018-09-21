"""Supervisr Invoke Tasks"""
import logging
import random
from glob import glob

from invoke import task
from invoke.terminals import WINDOWS

LOGGER = logging.getLogger(__name__)


@task
# pylint: disable=unused-argument
def generate_secret_key(ctx):
    """Generate Django SECRET_KEY"""
    charset = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
    print(''.join([random.SystemRandom().choice(charset) for i in range(50)]))


@task
def clean(ctx):
    """Clean Python cached files"""
    ctx.run(r'find . -name *.pyc -exec rm -rf {} \;', warn=True)
    LOGGER.success('Cleaned python cache')
    ctx.run(r'find supervisr/cache/ -name *.djcache -exec rm -rf {} \;', warn=True)
    LOGGER.success('Cleaned django cache files')
    ctx.run(r'find supervisr/puppet/modules/ -name *.tgz -exec rm -rf {} \;', warn=True)
    LOGGER.success('Cleaned puppet modules')


@task
def compile_reqs(ctx):
    """Compile all requirements into one requirements.txt"""
    if WINDOWS:
        ctx.config.run.shell = "C:\\Windows\\System32\\cmd.exe"
    requirements = glob("supervisr/**/requirements.txt", recursive=True)
    requirements_dev = glob("supervisr/**/requirements-dev.txt", recursive=True)
    ctx.run("cat %s > requirements.txt" % ' '.join(requirements))
    ctx.run("cat %s > requirements-dev.txt" % ' '.join(requirements + requirements_dev))


@task
def build_static(ctx):
    """Build Static CSS and JS files and run collectstatic"""
    if WINDOWS:
        ctx.config.run.shell = "C:\\Windows\\System32\\cmd.exe"
    with ctx.cd('assets'):
        ctx.run('npm install')
        ctx.run('npm upgrade')
        if WINDOWS:
            ctx.run('.\\node_modules\\.bin\\grunt --no-color', hide='out')
        else:
            ctx.run('.node_modules/.bin/grunt --no-color', hide='out')
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
