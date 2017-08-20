"""
Supervisr Stats Graphite Client
"""

import logging
import socket
import time

from supervisr.core.models import Setting

LOGGER = logging.getLogger(__name__)

class GraphiteClient(object):
    """
    Simple Write-only Graphite CLient
    """

    host = ''
    port = 2003
    prefix = 'supervisr'

    _socket = None

    def __init__(self):
        """
        Load settings form DB
        """
        self.host = Setting.get('host')
        self.port = int(Setting.get('port'))
        self.prefix = Setting.get('prefix')

    def connect(self):
        """
        Connect to graphite socket
        """
        try:
            self._socket = socket.socket()
            self._socket.connect((self.host, self.port))
        except ConnectionRefusedError:
            raise GraphiteException('Connection refused')

    def write(self, key, value):
        """
        Write data to graphite
        """
        name = '.'.join([self.prefix, key])
        self._socket.send(str.encode("%s %d %d\n" % (name, value, time.time())))

    def close(self):
        """
        Close socket
        """
        self._socket.close()

    def __enter__(self):
        self.connect()
        return self

    # pylint: disable=unused-argument
    def __exit__(self, _type, value, _tb):
        self._socket.close()

class GraphiteException(Exception):
    """
    Exception wrapper to make catching easier
    """
    pass
