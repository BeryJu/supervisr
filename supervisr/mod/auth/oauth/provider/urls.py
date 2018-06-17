"""
Supervisr Mod LDAP urls
"""

from django.conf.urls import include, url
from supervisr.mod.auth.oauth.provider.views import oauth2

urlpatterns = [
    # Custom OAuth 2 Authorize View
    url(r'^authorize/$', oauth2.SupervisrAuthorizationView.as_view(),
        name="oauth2-authorize"),
    # OAuth API
    url(r'', include('oauth2_provider.urls', namespace='oauth2_provider')),
]
