"""Supervisr Puppet Apps Config"""

from supervisr.core.apps import SettingBootstrapper, SupervisrAppConfig


class SupervisrPuppetConfig(SupervisrAppConfig):
    """Supervisr Puppet app config"""

    name = 'supervisr.puppet'
    verbose_name = 'Supervisr Puppet'
    navbar_enabled = lambda self, request: request.user.is_superuser
    title_modifier = lambda self, request: 'Puppet'

    def bootstrap(self):
        settings = SettingBootstrapper()
        # TODO: Random string
        settings.add(key='url_key', value='test')
        return (settings, )
