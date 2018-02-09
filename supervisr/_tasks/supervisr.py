"""
Supervisr Invoke Dev Tasks
"""
import logging
import os
import random
from functools import wraps
from glob import glob

from invoke import task
from invoke.platform import WINDOWS

if WINDOWS:
    PYTHON_EXEC = 'python'
else:
    PYTHON_EXEC = 'python3'
LOGGER = logging.getLogger(__name__)

def shell(func):
    """Fixes the Shell on Windows Systems"""
    @wraps(func)
    def wrapped(ctx, *args, **kwargs):
        """
        Fixes the Shell on Windows Systems
        """
        if WINDOWS:
            ctx.config.run.shell = "C:\\Windows\\System32\\cmd.exe"
        return func(ctx, *args, **kwargs)
    return wrapped

@task
def build_static(ctx):
    """Build Static CSS and JS files and run collectstatic"""
    if WINDOWS:
        ctx.config.run.shell = "C:\\Windows\\System32\\cmd.exe"
    with ctx.cd('assets'):
        ctx.run('grunt --no-color', hide='out')
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])

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
# pylint: disable=unused-argument
def generate_secret_key(ctx):
    """Generate Django SECRET_KEY"""
    print(''.join([random.SystemRandom() \
            .choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)]))

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
@shell
def prospector(ctx):
    """Run prospector"""
    ctx.run("prospector")

@task
@shell
def isort(ctx):
    """Run isort"""
    ctx.run("isort -c -vb -sg env -b importlib")

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

# Some tasks to make full testing easier
@task(pre=[coverage, isort, lint, prospector, unittest])
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
    ctx.run("%s supervisr --html --html-dir=\"docgen\""
            " --html-no-source  --overwrite --docstring-style=google" % tool)
