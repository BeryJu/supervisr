"""
Supervisr Core V1 API Urls
"""

from django.conf.urls import url

from supervisr.core.api.v1.accounts import AccountAPI
from supervisr.core.api.v1.domains import DomainAPI
from supervisr.core.api.v1.events import EventAPI
from supervisr.core.api.v1.providers import ProviderAPI
from supervisr.core.api.v1.system import SystemAPI

urlpatterns = [
    url(r'^accounts/(?P<verb>\w+)/$', AccountAPI.as_view(), name='accounts'),
    url(r'^domains/(?P<verb>\w+)/$', DomainAPI.as_view(), name='domains'),
    url(r'^events/(?P<verb>\w+)/$', EventAPI.as_view(), name='events'),
    url(r'^providers/(?P<verb>\w+)/$', ProviderAPI.as_view(), name='providers'),
    url(r'^system/(?P<verb>\w+)/$', SystemAPI.as_view(), name='system'),
]
