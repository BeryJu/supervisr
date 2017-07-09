"""
Supervisr Static Apps Config
"""
import logging

from django.db.utils import InternalError, OperationalError, ProgrammingError

from supervisr.core.apps import SupervisrAppConfig

LOGGER = logging.getLogger(__name__)

class SupervisrStaticConfig(SupervisrAppConfig):
    """
    Supervisr Static app config
    """

    name = 'supervisr.static'
    label = 'supervisr/static'
    verbose_name = 'Supervisr Static'
    navbar_enabled = lambda self, request: False

    def ready(self):
        super(SupervisrStaticConfig, self).ready()
        try:
            self.update_filepages()
        except (OperationalError, ProgrammingError, InternalError):
            pass

    # pylint: disable=no-self-use
    def update_filepages(self):
        """
        Update all FilePages from File
        """
        from supervisr.static.models import FilePage
        count = 0
        for fpage in FilePage.objects.all():
            if fpage.update_from_file():
                LOGGER.debug("Successfully updated %s with '%s'", fpage.title, fpage.path)
                count += 1
        LOGGER.info("Successfully updated %d FilePages", count)