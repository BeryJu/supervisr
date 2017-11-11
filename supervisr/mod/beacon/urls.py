"""Supervisr Beacon URLs"""

from django.conf.urls import url

# from supervisr.mod.beacon.views import receiver
from supervisr.mod.beacon.api.PulseAPI import PulseAPI

urlpatterns = [
    # url(r'^receive/$', receiver.receive, name='recieve'),
    url(r'^pulse/(?P<verb>\w+)/$', PulseAPI.as_view(), name='api-pulse'),
]
