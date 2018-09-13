"""Supervisr Core v1 API Urls"""

from django.conf.urls import url

from supervisr.core.utils.constants import UUID_REGEX
from supervisr.dns.api.v1.record import RecordAPI, dyndns_update
from supervisr.dns.api.v1.zone import ZoneAPI

urlpatterns = [
    url(r'^records/(?P<verb>\w+)/$', RecordAPI.as_view(), name='api-v1-records'),
    url(r'^records/(?P<record_uuid>%s)/dyndns/$' % UUID_REGEX,
        dyndns_update, name='api-v1-zone-dyndns'),
    url(r'^zones/(?P<verb>\w+)/$', ZoneAPI.as_view(), name='api-v1-zone'),
]
