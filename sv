#!/usr/bin/env python3
# flake8: noqa
"""Supervisr launcher script. This file is run outside of the virtualenv, thus no extra
packages are available here."""
import os
import subprocess
import sys

virtual_env_name = 'env'
is_packaged = False
command = ""

def call(command):
    """Call command, redirect stdout and stderr"""
    return subprocess.call(command, shell=True)


def activate_virtual_env():
    """Load virtualenv"""
    activate_this_file = os.path.realpath('%s/bin/activate_this.py' % virtual_env_name)
    exec(open(activate_this_file).read(), dict(__file__=activate_this_file))


def bootstrap_django():
    """Bootstrap pymysql and django"""
    import pymysql
    pymysql.install_as_MySQLdb()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supervisr.core.settings")
    os.environ.setdefault("SUPERVISR_ENV", "local")


# Check if this file is a symlink, and if so change to real base dir
base_dir = os.path.dirname(os.path.realpath(__file__))
if base_dir != os.getcwd() and not base_dir.endswith('%s/bin' % virtual_env_name):
    os.chdir(base_dir)
    is_packaged = True

os.environ['SUPERVISR_PACKAGED'] = str(is_packaged)

if len(sys.argv) < 2:
    # No Arguments passed, show list of all possible arguments
    command = 'invoke --list'
else:
    # If first argument is 'manage', launch that during django so manage.py isn't needed
    if sys.argv[1] == 'manage':
        # Remove first two argument since that's `sv manage`
        args = sys.argv.copy()[1:]
        activate_virtual_env()
        bootstrap_django()
        from django.core.management import execute_from_command_line
        sys.exit(execute_from_command_line(args))
    # Pass commands to invoke
    # Remove first argument since that's `sv`
    args = sys.argv.copy()[1:]
    command = 'invoke %s' % ' '.join(args)

if is_packaged:
    # Script needs to be run as root since we use `su` to change user
    if os.getuid() != 0:
        sys.stderr.write('This script must be run as root\n')
        sys.stderr.flush()
        sys.exit(1)
    # We are root so we can change users
    call('/bin/su -s /bin/bash -c "'
         'cd %s && source env/bin/activate && %s && deactivate'
         '" supervisr' % (base_dir, command))
else:
    if 'VIRTUAL_ENV' in os.environ:
        # Virtualenv is already enabled, just execute command
        call(command)
    else:
        call('source env/bin/activate && %s && deactivate' % command)
