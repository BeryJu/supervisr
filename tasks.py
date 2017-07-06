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
    if WINDOWS:
        ctx.config.run.shell = "C:\\Windows\\System32\\cmd.exe"
    requirements = glob("supervisr/**/requirements.txt")
    requirements.extend(glob("supervisr/**/**/requirements.txt"))
    requirements.extend(glob("supervisr/**/**/**/requirements.txt"))
    requirements.extend(glob("supervisr/**/**/**/**/requirements.txt"))
    if dev:
        requirements.extend(glob("supervisr/**/requirements-dev.txt"))
        requirements.extend(glob("supervisr/**/**/requirements-dev.txt"))
        requirements.extend(glob("supervisr/**/**/**/requirements-dev.txt"))
        requirements.extend(glob("supervisr/**/**/**/**/requirements-dev.txt"))
    ctx.run("pip3 install -U -r %s" % ' -r '.join(requirements))

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
    Run(modules)

@task
@shell
def prospector(ctx):
    """
    Run prospector
    """
    ctx.run("prospector")

@task
@shell
def isort(ctx):
    """
    Run isort
    """
    ctx.run("isort -c -vb -sg env -b importlib")

@task()
@shell
def coverage(ctx):
    """
    Run Unittests and get coverage
    """
    ctx.run("coverage run manage.py test --pattern=Test*.py")
    ctx.run("coverage report")

@task
@shell
def unittest(ctx):
    """
    Run Unittests
    """
    ctx.run("%s manage.py test --pattern=Test*.py" % PYTHON_EXEC)

# Some tasks to make full testing easier
@task(pre=[coverage, isort, lint, prospector])
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
    for gen in glob('docs/source/supervisr**'):
        os.remove(gen)
    os.remove('docs/source/modules.rst')
    shutil.rmtree('docs/build', ignore_errors=True)
    print("Cleaned!")
    for module in glob('supervisr/**/'):
        ctx.run('sphinx-apidoc -o docs/source %s' % module)
    ctx.run('sphinx-build -b html docs/source docs/build')
