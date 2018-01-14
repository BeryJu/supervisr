"""
Supervisr Puppet Apps Config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrPuppetConfig(SupervisrAppConfig):
    """
    Supervisr Puppet app config
    """

    name = 'supervisr.puppet'
    verbose_name = 'Supervisr Puppet'
    navbar_enabled = lambda self, request: request.user.is_superuser
    title_modifier = lambda self, request: 'Puppet'

    def ensure_settings(self):
        """ensure puppet settings"""
        from supervisr.core.models import get_random_string
        return {
            'url_key': get_random_string(20),
        }
