"""Supervisr Stats Influx AppConfig"""

from supervisr.core.apps import SettingBootstrapper, SupervisrAppConfig


class SupervisrModStatInfluxConfig(SupervisrAppConfig):
    """Supervisr Influx AppConfig"""

    name = 'supervisr.mod.stats.influx'
    admin_url_name = 'supervisr_mod_stats_influx:admin_settings'
    label = 'supervisr_mod_stats_influx'
    verbose_name = 'Supervisr mod_stats_influx'
    title_modifier = lambda self, request: 'Stats/Influx'

    def bootstrap(self):
        settings = SettingBootstrapper()
        settings.add(key='enabled', value=False)
        settings.add(key='host', value='localhost')
        settings.add(key='port', value=8086)
        settings.add(key='database', value='supervisr')
        settings.add(key='username', value='root')
        settings.add(key='password', value='root')
        return (settings, )
