"""supervisr mod/beacon API v1 URLs"""
from django.conf.urls import url

from supervisr.mod.beacon.api.v1.pulse import PulseAPI

urlpatterns = [
    url(r'^pulse/(?P<verb>\w+)/$', PulseAPI.as_view(), name='pulse'),
]
