"""Supervisr Core V1 API Urls"""

from django.conf.urls import url

from supervisr.core.api.v1.accounts import AccountAPI, http_basic_auth
from supervisr.core.api.v1.credentials import CredentialAPI
from supervisr.core.api.v1.domains import DomainAPI
from supervisr.core.api.v1.events import EventAPI
from supervisr.core.api.v1.providers import ProviderAPI
from supervisr.core.api.v1.system import SystemAPI
from supervisr.core.api.v1.tasks import TaskAPI

urlpatterns = [
    url(r'^accounts/http_basic_auth/$', http_basic_auth, name='accounts-http-basic-auth'),
    url(r'^accounts/(?P<verb>\w+)/$', AccountAPI.as_view(), name='accounts'),
    url(r'^credentials/(?P<verb>\w+)/$', CredentialAPI.as_view(), name='credentials'),
    url(r'^domains/(?P<verb>\w+)/$', DomainAPI.as_view(), name='domains'),
    url(r'^events/(?P<verb>\w+)/$', EventAPI.as_view(), name='events'),
    url(r'^providers/(?P<verb>\w+)/$', ProviderAPI.as_view(), name='providers'),
    url(r'^system/(?P<verb>\w+)/$', SystemAPI.as_view(), name='system'),
    url(r'^tasks/(?P<verb>\w+)/$', TaskAPI.as_view(), name='tasks'),
]

# from rest_framework import routers
# from supervisr.core.api.v1.credentials import CredentialViewSet

# core_router = routers.DefaultRouter()
# core_router.register(r'userpasswordcredential', CredentialViewSet)
# urlpatterns = core_router.urls
