"""
Supervisr Core Middleware to detect Maintenance Mode
"""

import time

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.urls import resolve
from django.utils.translation import ugettext_lazy as _
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError
from requests.exceptions import ConnectionError as reqConnectionError
from supervisr.core.models import Setting
from supervisr.core.utils import get_remote_ip, get_reverse_dns
from supervisr.mod.stats.influx.influx_client import InfluxClient


def stats(get_response):
    """Middleware get stats"""

    def middleware(request: HttpRequest) -> HttpResponse:
        """Middleware get stats"""
        before = time.time()
        response = get_response(request)
        after = time.time()

        if Setting.get_bool('enabled'):
            try:
                with InfluxClient() as client:
                    res_match = resolve(request.path_info).func
                    view_path = (res_match.__module__ + '.' + res_match.__name__)
                    remote_ip = get_remote_ip(request)
                    reverse_dns = get_reverse_dns(remote_ip)
                    username = 'Anonymous' if request.user.username == '' else request.user.username
                    client.write('request',
                                 tags={
                                     'view_path': view_path,
                                     'remote_ip': remote_ip,
                                     'remote_ip_rdns': reverse_dns,
                                     'user': username,
                                 },
                                 duration=(after - before) * 1000,
                                 status=response.status_code)
            except (InfluxDBClientError, InfluxDBServerError, reqConnectionError, IOError) as exc:
                if request.user.is_authenticated and request.user.is_superuser:
                    # Only show message if logged in and superuser
                    messages.error(request, _("Influx Error: %(msg)s" % {'msg': repr(exc)}))
        return response
    return middleware
