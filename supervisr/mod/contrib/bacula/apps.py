"""
Supervisr Bacula Apps Config
"""
import logging

from supervisr.core.apps import SupervisrAppConfig

LOGGER = logging.getLogger(__name__)

class SupervisrModContribBaculaConfig(SupervisrAppConfig):
    """
    Supervisr Bacula app config
    """

    name = 'supervisr.mod.contrib.bacula'
    label = 'supervisr/mod/contrib/bacula'
    verbose_name = 'Supervisr Bacula'
    navbar_enabled = lambda self, request: request.user.is_superuser
    title_moddifier = lambda self, title, request: 'Bacula'
