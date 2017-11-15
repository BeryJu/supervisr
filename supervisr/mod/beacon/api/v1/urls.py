"""supervisr mod/beacon API v1 URLs"""
from django.conf.urls import url

# from supervisr.mod.beacon.views import receiver
from supervisr.mod.beacon.api.v1.pulse import PulseAPI

urlpatterns = [
    # url(r'^receive/$', receiver.receive, name='receive'),
    url(r'^pulse/(?P<verb>\w+)/$', PulseAPI.as_view(), name='pulse'),
]