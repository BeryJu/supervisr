"""supervisr core test runner"""

# This file mainly exists to allow python setup.py test to work.
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supervisr.core.settings")
os.environ.setdefault("SUPERVISR_LOCAL_SETTINGS", "supervisr.local_settings")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def runtests():
    """Run all django tests"""
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'test'])


if __name__ == '__main__':
    runtests()
