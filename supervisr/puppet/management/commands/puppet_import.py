"""Supervisr Puppet Import"""

import logging

from django.core.management.base import BaseCommand

from supervisr.puppet.utils import ForgeImporter

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """Import a module from puppetforge"""

    help = 'Import a module from puppetforge'

    def add_arguments(self, parser):
        parser.add_argument('--module', type=str, action='append', required=True)

    def handle(self, *args, **options):
        importer = ForgeImporter()
        for module in options.get('module'):
            importer.import_module(module)
        LOGGER.success("Done!")
