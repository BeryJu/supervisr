"""
Supervisr Static Apps Config
"""
import logging

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
        self.update_filepages()

    # pylint: disable=no-self-use
    def update_filepages(self):
        """
        Update all FilePages from File
        """
        from supervisr.static.models import FilePage
        for fpage in FilePage.objects.all():
            fpage.update_from_file()
            LOGGER.debug("Successfully updated %s with '%s'", fpage.title, fpage.path)
        LOGGER.info("Successfully updated %d FilePages", len(FilePage.objects.all()))
