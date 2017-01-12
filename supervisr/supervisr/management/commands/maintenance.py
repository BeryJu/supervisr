from django.core.management.base import BaseCommand, CommandError
from ...models import *
import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Turns maintenance Mode on or off'

    def add_arguments(self, parser):
        parser.add_argument('state', type=str)

    def handle(self, *args, **options):
        value = options['state'].lower() in ('on', 'true', 'yes')

        setting, created = Setting.objects.get_or_create(
            key='supervisr:maintenancemode',
            defaults= {'value': 'False'})
        setting.set_bool(value)
        setting.save()
        word = 'Enabled' if value is True else 'Disabled'
        logger.info("%s maintenance mode." % word)