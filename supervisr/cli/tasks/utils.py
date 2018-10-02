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
def compile_requirements(ctx):
    """Compile all requirements into one requirements.txt"""
    if WINDOWS:
        ctx.config.run.shell = "C:\\Windows\\System32\\cmd.exe"
    requirements = glob("supervisr/**/requirements.txt", recursive=True)
    requirements_dev = glob("supervisr/**/requirements-dev.txt", recursive=True)
    ctx.run("cat %s > requirements.txt" % ' '.join(requirements))
    ctx.run("cat %s > requirements-dev.txt" % ' '.join(requirements + requirements_dev))
