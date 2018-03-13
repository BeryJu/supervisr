"""Supervisr Stats Influx AppConfig"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModStatInfluxConfig(SupervisrAppConfig):
    """Supervisr Influx AppConfig"""

    name = 'supervisr.mod.stats.influx'
    admin_url_name = 'supervisr_mod_stats_influx:admin_settings'
    label = 'supervisr_mod_stats_influx'
    verbose_name = 'Supervisr mod_stats_influx'
    title_modifier = lambda self, request: 'Stats/Influx'

    def ensure_settings(self):
        return {
            'enabled': False,
            'host': 'localhost',
            'port': 8086,
            'database': 'supervisr',
            'username': 'root',
            'password': 'root',
        }
