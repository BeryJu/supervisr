"""Supervisr Core Maintenance ManagementCommand"""

import logging

from django.core.management.base import BaseCommand

from supervisr.core.models import Setting

LOGGER = logging.getLogger(__name__)

class Command(BaseCommand):
    """Turns maintenance Mode on or off via manage.py"""

    help = 'Turns maintenance Mode on or off'

    def add_arguments(self, parser):
        parser.add_argument('state', type=str)

    def handle(self, *args, **options):
        value = options['state'].lower() in ('on', 'true', 'yes')

        setting = Setting.objects.get_or_create(
            key='maintenancemode',
            namespace='supervisr.core',
            defaults={'value': 'False'})[0]
        setting.value = value
        setting.save()
        word = 'Enabled' if value is True else 'Disabled'
        LOGGER.debug("%s maintenance mode.", word)
