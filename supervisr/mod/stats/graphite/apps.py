"""
Supervisr Stats Graphite AppConfig
"""

import logging
import os
import socket
import threading
import time

import psutil
from django.conf import settings

from supervisr.core.apps import SupervisrAppConfig

LOGGER = logging.getLogger(__name__)

class SupervisrModStatGraphiteConfig(SupervisrAppConfig):
    """
    Supervisr TFA AppConfig
    """

    name = 'supervisr.mod.stats.graphite'

    def ready(self):
        super(SupervisrModStatGraphiteConfig, self).ready()

        def send_stats(client, host):
            """
            Statistics checker function
            """
            process = psutil.Process(os.getpid())
            client.write('%s.mem' % host, process.memory_info().rss / 1024 / 1024)
            client.write('%s.cpu' % host, process.cpu_percent())
            time.sleep(10)
            send_stats(client, host)

        from supervisr.core.models import Setting
        from supervisr.mod.stats.graphite.graphite_client import GraphiteClient

        if Setting.get('mod:stats:graphite:enabled', 'False') != 'False':
            if settings.DEBUG:
                LOGGER.info("Not starting StatsThread because DEBUG")
            else:
                client = GraphiteClient()
                thread = threading.Thread(target=send_stats,
                                          args=(client, socket.gethostname(), ))
                thread.start()
                LOGGER.info("Started Statistics sender in seperate Thread")
