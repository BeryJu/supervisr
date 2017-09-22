"""
Supervisr Core r1 API Urls
"""

from django.conf.urls import url

from supervisr.core.regex import DOMAIN_REGEX
from supervisr.dns.views.api.r1.record import RecordAPI, dyndns_update
from supervisr.dns.views.api.r1.zone import ZoneAPI

urlpatterns = [
    url(r'^records/(?P<verb>\w+)/$', RecordAPI.as_view(), name='api-r1-records'),
    url(r'^records/(?P<zone>%s)/(?P<record>.+)/dyndns/$' % DOMAIN_REGEX,
        dyndns_update, name='api-r1-zone-dyndns'),
    url(r'^zones/(?P<verb>\w+)/$', ZoneAPI.as_view(), name='api-r1-zone'),
]
