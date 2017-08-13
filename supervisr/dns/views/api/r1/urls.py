"""
Supervisr Core r1 API Urls
"""

from django.conf.urls import url

from supervisr.dns.views.api.r1.records import RecordAPI
from supervisr.dns.views.api.r1.zones import ZoneAPI

urlpatterns = [
    url(r'^records/(?P<verb>\w+)/$', RecordAPI.as_view(), name='api-r1-records'),
    url(r'^zones/(?P<verb>\w+)/$', ZoneAPI.as_view(), name='api-r1-zone'),
]
