"""Supervisr Core v1 API Urls"""

from django.conf.urls import url

from supervisr.core.utils.constants import UUID_REGEX
from supervisr.dns.api.v1.record import DataRecordAPI, SetRecordAPI, dyndns_update
from supervisr.dns.api.v1.zone import ReverseZoneAPI, ZoneAPI

urlpatterns = [
    url(r'^records/data/(?P<verb>\w+)/$', DataRecordAPI.as_view(), name='api-v1-data-records'),
    url(r'^records/set/(?P<verb>\w+)/$', SetRecordAPI.as_view(), name='api-v1-set-records'),
    url(r'^records/(?P<record_uuid>%s)/dyndns/$' % UUID_REGEX,
        dyndns_update, name='api-v1-zone-dyndns'),
    url(r'^zones/(?P<verb>\w+)/$', ZoneAPI.as_view(), name='api-v1-zone'),
    url(r'^zones/reverse/(?P<verb>\w+)/$', ReverseZoneAPI.as_view(), name='api-v1-reverse-zone'),
]
