"""
Supervisr Core Cleanup ManagementCommand
"""

import logging

from django.core.management.base import BaseCommand

from ...models import PurgeableModel

LOGGER = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Wipes all Purgeable Models
    """

    help = 'Wipes all Instances of PurgeableModel'

    def handle(self, *args, **options):
        # pylint: disable=no-member
        classes = PurgeableModel.__subclasses__()
        for cls in classes:
            LOGGER.info("Purging %s", cls.__name__)
            cls_inst = cls.objects.all()
            for pm_inst in cls_inst:
                pm_inst.purge()
            LOGGER.info("Deleted %s models", len(cls_inst))
