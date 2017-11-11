"""
Supervisr Core V1 API Urls
"""

from django.conf.urls import url

from supervisr.core.api.v1 import system, user
from supervisr.core.api.v1.domains import DomainAPI
from supervisr.core.api.v1.providers import ProviderAPI

urlpatterns = [
    url(r'^account/me/$', user.account_me, name='user-account_me'),
    url(r'^domains/(?P<verb>\w+)/$', DomainAPI.as_view(), name='domains'),
    url(r'^providers/(?P<verb>\w+)/$', ProviderAPI.as_view(), name='providers'),
    url(r'^system/health/$', system.health, name='system-health'),
]
