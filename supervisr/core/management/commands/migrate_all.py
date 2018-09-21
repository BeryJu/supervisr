"""Supervisr Core migrate_all ManagementCommand"""
from logging import getLogger

from django.conf import settings
from django.core.management.base import BaseCommand

from supervisr.core.views.setup import SetupWizard

LOGGER = getLogger(__name__)


class Command(BaseCommand):
    """Apply Migrations for all databases"""

    help = 'Apply Migrations for all databases'

    def handle(self, *args, **options):
        wizard = SetupWizard()
        for db_alias in settings.DATABASES.keys():
            wizard.run_migrate(db_alias=db_alias)
        if wizard.migration_progress == {}:
            LOGGER.success("No migrations to apply!")
