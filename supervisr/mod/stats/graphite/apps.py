"""
Supervisr Stats Graphite AppConfig
"""

import logging
import os
import socket

import psutil
from django.dispatch import receiver

from supervisr.core.apps import SupervisrAppConfig
from supervisr.core.thread.background import SIG_GET_SCHEDULER

LOGGER = logging.getLogger(__name__)

class SupervisrModStatGraphiteConfig(SupervisrAppConfig):
    """
    Supervisr TFA AppConfig
    """

    name = 'supervisr.mod.stats.graphite'
    admin_url_name = 'supervisr/mod/stats/graphite:admin_settings'
    label = 'supervisr/mod/stats/graphite'
    title_moddifier = lambda self, title, request: 'Stats/Graphite'

    def __init__(self, *args, **kwargs):
        super(SupervisrModStatGraphiteConfig, self).__init__(*args, **kwargs)
        @receiver(SIG_GET_SCHEDULER)
        # pylint: disable=unused-argument
        def handle_stats_graphite(sender, scheduler, **kwargs):
            """
            Register Schedule handler
            """
            from supervisr.core.models import Setting
            from supervisr.mod.stats.graphite.graphite_client import GraphiteClient

            client = GraphiteClient()

            def send_stats(client, host):
                """
                Statistics checker function
                """
                def send():
                    """
                    Send CPU and Memory usage
                    """
                    process = psutil.Process(os.getpid())
                    client.write('server.%s.mem' % host, process.memory_info().rss / 1024 / 1024)
                    client.write('server.%s.cpu' % host, process.cpu_percent())
                return send

            if Setting.get('enabled', default='False') != 'False':
                client.connect()
                scheduler.every(10).seconds.do(send_stats(client, socket.gethostname()))

    def ensure_settings(self):
        return {
            'enabled': False,
            'host': 'localhost',
            'port': 2003,
            'prefix': 'supervisr',
        }
