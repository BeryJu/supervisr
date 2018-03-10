"""Supervisr Core Setting ManagementCommand"""

import logging
from argparse import ArgumentParser

from django.core.management.base import BaseCommand

from supervisr.core.models import Setting

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """Edit settings via manage.py"""

    help = 'Edit settings'

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('-vo', '--value-only', action='store_true')
        parser.add_argument('action', type=str, choices=['get', 'getall', 'list', 'set'])
        parser.add_argument('keypath', type=str, nargs='?')
        parser.add_argument('value', type=str, nargs='?')

    def handle(self, *args, **options):
        getattr(self, options['action'], None)(**options)

    # pylint: disable=unused-argument
    def getall(self, **kwargs):
        """print all namespace keys with values"""
        for setting in Setting.objects.all().order_by('namespace', 'key'):
            print("%-50s: %s" % ("%s/%s" % (setting.namespace, setting.key), setting.value))

    # pylint: disable=unused-argument
    def list(self, **kwargs):
        """List namespace keys"""
        for setting in Setting.objects.all().order_by('namespace', 'key'):
            print("%-50s: %s" % ("%s/%s" % (setting.namespace, setting.key), setting.value))

    def get(self, **kwargs):
        """Show single setting"""
        if not kwargs.get('keypath'):
            raise ValueError('keypath argument required for get.')
        namespace, key = kwargs.get('keypath').split('/')
        setting = Setting.objects.get(namespace=namespace, key=key)
        if kwargs.get('value_only'):
            print(setting.value)
        else:
            print("%-50s: %s" % ("%s/%s" % (setting.namespace, setting.key), setting.value))

    def set(self, **kwargs):
        """Set a single setting"""
        if not kwargs.get('keypath'):
            raise ValueError('keypath argument required for get.')
        namespace, key = kwargs.get('keypath').split('/')
        setting = Setting.objects.get(namespace=namespace, key=key)
        setting.set(kwargs.get('value'))
        self.get(**kwargs)
