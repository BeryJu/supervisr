"""Supervisr Core Middleware to time requests"""
from functools import reduce
from operator import add
from time import time

from django.conf import settings
from django.db import connection
from django.http import HttpRequest, HttpResponse
from django.http.response import StreamingHttpResponse
from django.urls import resolve

from supervisr.core.utils import get_remote_ip, get_reverse_dns
from supervisr.core.utils.statistics import StatisticType, set_statistic


def statistic_middleware(get_response):
    """Middleware get stats"""

    def middleware(request: HttpRequest) -> HttpResponse:
        """Middleware get stats"""
        if not settings.DEBUG:
            return get_response(request)
        # get number of db queries before we do anything
        before_queries = len(connection.queries)

        # time the view
        start = time()
        response = get_response(request)
        total_time = time() - start

        # compute the db time for the queries just run
        db_queries = len(connection.queries) - before_queries
        if db_queries:
            db_time = reduce(add, [float(q['time'])
                                   for q in connection.queries[before_queries:]])
        else:
            db_time = 0.0

        # and backout python time
        python_time = total_time - db_time
        # Gather other metadata
        res_match = resolve(request.path_info).func
        view_path = (res_match.__module__ + '.' + res_match.__name__)
        remote_ip = get_remote_ip(request)
        reverse_dns = get_reverse_dns(remote_ip)
        set_statistic('request',
                      hints={
                          'status': response.status_code,
                          'view_path': view_path,
                          'remote_ip': remote_ip,
                          'remote_ip_reverse': reverse_dns,
                          'user_authenticated': request.user.is_authenticated,
                      },
                      status={
                          'value': response.status_code,
                          'type': StatisticType.AsIs,
                      },
                      total_time={
                          'value': total_time * 1000,
                          'type': StatisticType.Timing,
                      },
                      python_time={
                          'value': python_time * 1000,
                          'type': StatisticType.Timing,
                      },
                      db_time={
                          'value': db_time * 1000,
                          'type': StatisticType.Timing,
                      },
                      db_queries={
                          'value': db_queries,
                          'type': StatisticType.AsIs
                      })
        # replace the comment if found
        if response and not isinstance(response, StreamingHttpResponse):
            if response.content:
                response.content = response.content.replace(
                    b'||TIMING||', str.encode(str(int(total_time * 1000))))
        return response
    return middleware
