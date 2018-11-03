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
exit_code = 0

def call(command):
    """Call command, redirect stdout and stderr"""
    return subprocess.call(command, shell=True)


def activate_virtual_env():
    """Load virtualenv"""
    if in_virtualenv:
        activate_this_file = os.path.realpath('%s/bin/activate_this.py' % virtual_env_name)
        exec(open(activate_this_file).read(), dict(__file__=activate_this_file))


def bootstrap_django():
    """Bootstrap pymysql and django"""
    import pymysql
    pymysql.install_as_MySQLdb()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supervisr.core.settings")
    os.environ.setdefault("SUPERVISR_ENV", "local")


def django(*args):
    """Run args with django"""
    from django.core.management import execute_from_command_line
    args = list(args)
    args[0] = 'sv manage'
    return execute_from_command_line(args)


def wrap_virtualenv(command):
    """Wrap command with `source ...activate`, but only if virtualenv is used."""
    # If we're packaged, change to correct directory first
    prefix = ''
    if is_packaged:
        prefix = 'cd %s &&' % base_dir
    if in_virtualenv:
        return '/bin/bash -c "%s source %s/bin/activate && %s && deactivate"' % (prefix,
                                                                                 virtual_env_name,
                                                                                 command)
    return '/bin/bash -c "%s"' % command

def pip(*args):
    """Run args with pip"""
    return call(wrap_virtualenv('pip %s' % ' '.join(args)))


# Check if this file is a symlink, and if so change to real base dir
base_dir = os.path.dirname(os.path.realpath(__file__))
if base_dir != os.getcwd() and not base_dir.endswith('%s/bin' % virtual_env_name):
    os.chdir(base_dir)
    is_packaged = True

in_virtualenv = os.path.exists('%s/bin/activate' % virtual_env_name)
os.environ['SUPERVISR_PACKAGED'] = str(is_packaged)

if len(sys.argv) < 2:
    # No Arguments passed, show list of all possible arguments
    command = 'invoke --list'
else:
    args = sys.argv.copy()[1:]
    # If first argument is 'manage', launch that during django so manage.py isn't needed
    if sys.argv[1] == 'manage':
        # Remove first two argument since that's `sv manage`
        activate_virtual_env()
        bootstrap_django()
        sys.exit(django(*args))
    # If first argument is pip, launch pip after removing first arg
    elif sys.argv[1] == 'pip':
        activate_virtual_env()
        # Remove first argument since pip doesnt expect the first argument to be `pip`
        sys.exit(pip(*args[1:]))
    # Pass commands to invoke
    command = 'invoke %s' % ' '.join(args)

if is_packaged:
    # Script needs to be run as root since we use `su` to change user
    if os.getuid() != 0:
        sys.stderr.write('This script must be run as root\n')
        sys.stderr.flush()
        sys.exit(1)
    # We are root so we can change users
    inner_command = wrap_virtualenv(command)
    exit_code = call('/bin/su -s %s supervisr' % inner_command)
else:
    if 'VIRTUAL_ENV' in os.environ:
        # Virtualenv is already enabled, just execute command
        exit_code = call(command)
    else:
        exit_code = call(wrap_virtualenv(command))
sys.exit(exit_code)
