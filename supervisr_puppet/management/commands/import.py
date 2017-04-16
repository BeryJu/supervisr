"""
Supervisr Puppet Import
"""

import logging

from django.core.management.base import BaseCommand

from ...utils import ForgeImporter

LOGGER = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Import a module from puppetforge
    """

    help = 'Import a module from puppetforge'

    # def add_arguments(self, parser):
    #     parser.add_argument('state', type=str)

    def handle(self, *args, **options):
        i = ForgeImporter()
        i.import_module('puppetlabs-apt')
        i.import_module('puppetlabs-ntp')
        i.import_module('puppetlabs-stdlib')
        print("Done!")
