"""Supervisr Stats Influx Client"""
from collections import MutableMapping
from logging import getLogger
from socket import getfqdn

from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError

from supervisr.core.models import Setting

LOGGER = getLogger(__name__)


# pylint: disable=too-many-instance-attributes
class InfluxClient:
    """Simple Write-only Influx CLient"""

    host = ''
    port = 8086
    username = 'root'
    password = '' # nosec
    database = 'supervisr'

    _fqdn = None
    _install_id = ''
    __client = None

    def __init__(self):
        """Load settings form DB"""
        self.host = Setting.get('host')
        self.port = Setting.get_int('port')
        self.username = Setting.get('username')
        self.password = Setting.get('password')
        self.database = Setting.get('database')
        self._fqdn = getfqdn()
        self._install_id = Setting.get('install_id', namespace='supervisr.core')

    def connect(self):
        """create influxdbclient instance"""
        self.__client = InfluxDBClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            database=self.database,
            timeout=5)

    def __flatten(self, source, parent_key='', sep='.'):
        """Flatten dictionary from {'a': {'b': 'c'}} to {'a.b': 'c'}"""
        items = []
        for key, value in source.items():
            new_key = parent_key + sep + key if parent_key else key
            if isinstance(value, MutableMapping):
                items.extend(self.__flatten(value, new_key, sep=sep).items())
            else:
                items.append((new_key, value))
        return dict(items)

    def write(self, measurement, tags=None, **values):
        """Write data to influx"""
        if not tags:
            tags = {}
        all_tags = {
            'host': self._fqdn,
            'install_id': self._install_id,
        }
        all_tags.update(self.__flatten(tags))
        try:
            result = self.__client.write_points([
                {
                    'measurement': measurement,
                    'tags': all_tags,
                    'fields': values
                }
            ])
            LOGGER.debug('wrote %s', measurement)
            return result
        except InfluxDBClientError as exc:
            LOGGER.debug(exc)
            return False

    def close(self):
        """Close socket"""
        # self.__client.close()

    def __enter__(self):
        try:
            self.connect()
        except InfluxDBClientError:
            pass
        return self

    def __exit__(self, _type, value, _tb):
        self.close()
