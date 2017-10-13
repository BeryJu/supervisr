"""
Supervisr Stats Influx Client
"""

import logging
import socket

from influxdb import InfluxDBClient

from supervisr.core.models import Setting

LOGGER = logging.getLogger(__name__)

class InfluxClient(object):
    """
    Simple Write-only Influx CLient
    """

    host = ''
    port = 8086
    username = 'root'
    password = 'root'
    database = 'supervisr'

    _fqdn = None
    _client = None

    def __init__(self):
        """
        Load settings form DB
        """
        self.host = Setting.get('host')
        self.port = int(Setting.get('port'))
        self.username = Setting.get('username')
        self.password = Setting.get('password')
        self.database = Setting.get('database')
        self._fqdn = socket.getfqdn()

    def connect(self):
        """
        create influxdbclient instance
        """
        self._client = InfluxDBClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            database=self.database,
            timeout=5)

    def write(self, meas, tags=None, **fields):
        """
        Write data to influx
        """
        if not tags:
            tags = {}
        all_tags = {
            'host': self._fqdn,
            }
        all_tags.update(tags)
        return self._client.write_points([
            {
                'measurement': meas,
                'tags': all_tags,
                'fields': fields
            }
        ])

    def close(self):
        """
        Close socket
        """
        # self._client.close()

    def __enter__(self):
        self.connect()
        return self

    # pylint: disable=unused-argument
    def __exit__(self, _type, value, _tb):
        self.close()