"""
Supervisr Core Middleware to detect Maintenance Mode
"""

import time

from django.core.urlresolvers import resolve

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
                res_match = resolve(req.path_info).func
                view_path = (res_match.__module__ + '.' + res_match.__name__).replace('.', '::')
                client.write('views.%s.duration' % view_path, (after - before) * 1000)
        return response
    return middleware
