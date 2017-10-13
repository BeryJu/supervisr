"""
Supervisr Core r2 API Urls
"""

from django.conf.urls import url

from supervisr.core.views.api.r2 import core, user
from supervisr.core.views.api.r2.domains import DomainAPI
from supervisr.core.views.api.r2.providers import ProviderAPI

urlpatterns = [
    url(r'^core/health', core.health, name='api-r2-core-health'),
    url(r'^account/me', user.account_me, name='api-r2-user-account_me'),
    url(r'^domains/(?P<verb>\w+)/$', DomainAPI.as_view(), name='api-r2-domains'),
    url(r'^providers/(?P<verb>\w+)/$', ProviderAPI.as_view(), name='api-r2-providers'),
]
