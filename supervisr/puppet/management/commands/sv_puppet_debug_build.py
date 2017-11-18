"""
Supervisr Puppet Debug Builder
"""

import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from supervisr.core.models import User

from ...builder import ReleaseBuilder
from ...models import PuppetModule

LOGGER = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Build a Puppet Module without saving it to the DB
    """

    help = 'Build a Puppet Module without saving it to the DB'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--import-deps', type=bool, default=False)
        parser.add_argument('--module', type=str, action='append', required=True)

    def handle(self, *args, **options):
        for module in options['module']:
            if '-' in module:
                n_user, n_module = module.split('-')
            else:
                n_module = module
                n_user = settings.SYSTEM_USER_NAME
            p_user = User.objects.filter(username=n_user)
            if p_user.exists():
                p_module = PuppetModule.objects.filter(name=n_module, owner=p_user.first())
                if p_module.exists():
                    i = ReleaseBuilder(p_module.first())
                    i.build()
                    LOGGER.info("Built Module %s!", n_module)
                    return "Built Module %s!" % n_module
                LOGGER.warning("Module %s-%s doesn't exist!", n_user, n_module)
                return "Module %s-%s doesn't exist!" % (n_user, n_module)
            LOGGER.warning("User %s doesn't exist!", n_user)
            return "User %s doesn't exist!" % n_user
