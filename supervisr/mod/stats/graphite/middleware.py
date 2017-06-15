"""
Supervisr Core Middleware to detect Maintenance Mode
"""

import time

from supervisr.core.models import Setting
from supervisr.mod.stats.graphite.graphite_client import GraphiteClient


def stats(get_response):
    """
    Middleware get stats
    """

    def middleware(req):
        """
        Middleware get stats
        """
        before = time.time()
        response = get_response(req)
        after = time.time()

        if Setting.objects.get(pk='mod:stats:graphite:enabled').value_bool:
            with GraphiteClient() as client:
                client.write('views.duration', (after - before) * 1000)
        return response
    return middleware
