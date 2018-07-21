"""
Supervisr OAuth Provider V1 API Urls
"""

from django.conf.urls import url

from supervisr.mod.auth.oauth.provider.api.v1.accounts import OAuthAccountAPI

urlpatterns = [
    url(r'^accounts/(?P<verb>\w+)/$', OAuthAccountAPI.as_view(), name='oauth-accounts'),
]
