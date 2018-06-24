"""supervisr mod stats influx tasks"""
import os
from logging import getLogger

import psutil
from supervisr.core.celery import CELERY_APP
from supervisr.core.models import Setting
from supervisr.mod.stats.influx.influx_client import InfluxClient

LOGGER = getLogger(__name__)


@CELERY_APP.task(bind=True, hard_time_limit=10)
# pylint: disable=unused-argument
def push_influx_data(self):
    """push process data to influxdb"""
    if Setting.get_bool('enabled'):
        try:
            client = InfluxClient()
            client.connect()
            process = psutil.Process(os.getpid())
            result = client.write('server',
                                  memory=process.memory_info().rss / 1024 / 1024,
                                  cpu=process.cpu_percent())
            if result:
                LOGGER.debug('Successfully wrote Influx Process data.')
            else:
                LOGGER.debug("Influx server refused our data.")
        except (TimeoutError, ConnectionError, IOError):
            LOGGER.warning("Failed to connect to influx server '%s'.", Setting.get('host'))