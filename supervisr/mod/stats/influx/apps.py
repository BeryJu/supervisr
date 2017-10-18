"""
Supervisr Stats Influx AppConfig
"""

import logging
import os

import psutil

from supervisr.core.apps import SupervisrAppConfig
from supervisr.core.thread.background import SCHEDULER, catch_exceptions

LOGGER = logging.getLogger(__name__)

class SupervisrModStatInfluxConfig(SupervisrAppConfig):
    """
    Supervisr Influx AppConfig
    """

    name = 'supervisr.mod.stats.influx'
    admin_url_name = 'supervisr/mod/stats/influx:admin_settings'
    label = 'supervisr/mod/stats/influx'
    title_moddifier = lambda self, title, request: 'Stats/Influx'

    def ready(self):
        super(SupervisrModStatInfluxConfig, self).ready()
        from supervisr.core.models import Setting
        from supervisr.mod.stats.influx.influx_client import InfluxClient

        if Setting.get_bool('enabled'):
            try:
                client = InfluxClient()
                client.connect()

                @catch_exceptions()
                def send():
                    """
                    Send CPU and Memory usage
                    """
                    process = psutil.Process(os.getpid())
                    client.write('server',
                                 memory=process.memory_info().rss / 1024 / 1024,
                                 cpu=process.cpu_percent())

                SCHEDULER.every(10).seconds.do(send)

            except (TimeoutError, ConnectionError, IOError):
                LOGGER.warning("Failed to connect to influx server '%s'.", Setting.get('host'))

    def ensure_settings(self):
        return {
            'enabled': False,
            'host': 'localhost',
            'port': 8086,
            'database': 'supervisr',
            'username': 'root',
            'password': 'root',
        }
