"""
Supervisr Core Middleware to detect Maintenance Mode
"""

import time

from django.contrib import messages
from django.core.urlresolvers import resolve
from django.utils.translation import ugettext as _
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError

from supervisr.core.models import Setting
from supervisr.core.utils import get_remote_ip, get_reverse_dns
from supervisr.mod.stats.influx.influx_client import InfluxClient


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

        if Setting.get_bool('enabled'):
            try:
                with InfluxClient() as client:
                    res_match = resolve(req.path_info).func
                    view_path = (res_match.__module__ + '.' + res_match.__name__)
                    remote_ip = get_remote_ip(req)
                    reverse_dns = get_reverse_dns(remote_ip)
                    username = 'Anonymous' if req.user.username == '' else req.user.username
                    client.write('request',
                                 tags={
                                     'view_path': view_path,
                                     'remote_ip': remote_ip,
                                     'remote_ip_rdns': reverse_dns,
                                     'user': username,
                                 },
                                 duration=(after - before) * 1000,
                                 status=response.status_code)
            except (InfluxDBClientError, InfluxDBServerError) as exc:
                if req.user.is_authenticated and req.user.is_superuser:
                    # Only show message if logged in and superuser
                    messages.error(req, _("Influx Error: %(msg)s" % {'msg': str(exc)}))
        return response
    return middleware
