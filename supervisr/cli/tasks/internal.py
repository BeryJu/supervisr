"""supervisr internal tasks"""
import os
import shutil
import tempfile
import time
from glob import glob
from logging import getLogger

from invoke import task
from invoke.terminals import WINDOWS

LOGGER = getLogger(__name__)


@task
def compile_requirements(ctx):
    """Compile all requirements into one requirements.txt"""
    if WINDOWS:
        ctx.config.run.shell = "C:\\Windows\\System32\\cmd.exe"
    requirements = glob("supervisr/**/requirements.txt", recursive=True)
    requirements_dev = glob("supervisr/**/requirements-dev.txt", recursive=True)
    ctx.run("cat %s > requirements.txt" % ' '.join(requirements))
    ctx.run("cat %s > requirements-dev.txt" % ' '.join(requirements + requirements_dev))


@task
def bumpversion(ctx, level):
    """Run bumpversion, update changelog from git commits and open editor"""
    context = {}
    bump_out = ctx.run('bumpversion --allow-dirty --dry-run --list %s' % level, hide=True).stdout
    # Convert string of `a=b` to dictionary {'a': 'b'} (trim out last line cause it is blank)
    bump = {line.split('=')[0]: line.split('=')[1] for line in bump_out.split('\n')[:-1]}
    context['version'] = bump['new_version']
    # Create a bumpversion message, since we run `bumpversion` in dry-run
    # and we want to commit that message into the version bump
    context['bumpversion_message'] = bump['message'].format(**bump)
    context['author'] = ctx.run('git config --get user.name', hide=True).stdout
    context['author_email'] = ctx.run('git config --get user.email', hide=True).stdout
    # Git output has a newline at the end which we need to trim off
    context['author'] = context['author'].split('\n')[0]
    context['author_email'] = context['author_email'].split('\n')[0]
    # Get a list of all commits between now and the last tag
    context['log'] = ctx.run(
        "git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:'  * %s'",
        hide=True).stdout
    # Get current date, formatted debian compatible
    context['date'] = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime())
    template = """supervisr (%(version)s) unstable; urgency=medium

  * %(bumpversion_message)s
%(log)s

 -- %(author)s <%(author_email)s>  %(date)s

"""
    with open('CHANGELOG') as _file:
        current_changelog = _file.read()
    editing = template % context + current_changelog
    with tempfile.NamedTemporaryFile(mode='w') as _file:
        # Write template contents
        _file.write(editing)
        _file.flush()
        # Spawn Editor
        ctx.run(os.environ.get('EDITOR', 'vim') + ' ' + _file.name, pty=True)
        # Copy new file
        shutil.copyfile(_file.name, 'CHANGELOG')
    # Stage file to git and commit with bumpversion
    ctx.run('git add CHANGELOG')
    ctx.run('bumpversion --allow-dirty %s' % level)
