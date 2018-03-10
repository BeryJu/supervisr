"""
Supervisr Invoke Tasks
"""
import logging
import random
from glob import glob

from invoke import task
from invoke.platform import WINDOWS

try:
    import django
except ImportError:
    print("Django could not be imported")

LOGGER = logging.getLogger(__name__)


@task()
# pylint: disable=unused-argument
def list_users(ctx):
    """Show a list of all users"""
    django.setup()
    from supervisr.core.models import User
    users = User.objects.all().order_by('pk')
    LOGGER.info("Listing users...")
    for user in users:
        LOGGER.info("id=%d username=%s email=%s", user.pk, user.username, user.email)


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
    print('Cleaned python cache')
    ctx.run(r'find supervisr/cache/ -name *.djcache -exec rm -rf {} \;', warn=True)
    print('Cleaned django cache files')
    ctx.run(r'find supervisr/puppet/modules/ -name *.tgz -exec rm -rf {} \;', warn=True)
    print('Cleaned puppet modules')


@task
def compile_reqs(ctx):
    """Compile all requirements into one requirements.txt"""
    if WINDOWS:
        ctx.config.run.shell = "C:\\Windows\\System32\\cmd.exe"
    requirements = glob("supervisr/**/requirements.txt")
    requirements.extend(glob("supervisr/**/**/requirements.txt"))
    requirements.extend(glob("supervisr/**/**/**/requirements.txt"))
    requirements.extend(glob("supervisr/**/**/**/**/requirements.txt"))
    requirements_dev = glob("supervisr/**/requirements-dev.txt")
    requirements_dev.extend(glob("supervisr/**/**/requirements-dev.txt"))
    requirements_dev.extend(glob("supervisr/**/**/**/requirements-dev.txt"))
    requirements_dev.extend(glob("supervisr/**/**/**/**/requirements-dev.txt"))
    ctx.run("cat %s > requirements.txt" % ' '.join(requirements))
    ctx.run("cat %s > requirements-dev.txt" % ' '.join(requirements_dev))


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
