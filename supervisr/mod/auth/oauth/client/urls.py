"""
Supervisr auth oauth client urls
"""

from allaccess.views import OAuthCallback, OAuthRedirect
from django.conf.urls import url

from supervisr.mod.auth.oauth.client.views import oauth2

urlpatterns = [
    url(r'^callback/(?P<provider>supervisr)/$',
        oauth2.SupervisrOAuthCallback.as_view(), name='allaccess-callback'),

    url(r'^login/(?P<provider>(\w|-)+)/$', OAuthRedirect.as_view(), name='allaccess-login'),
    url(r'^callback/(?P<provider>(\w|-)+)/$', OAuthCallback.as_view(), name='allaccess-callback'),
]
