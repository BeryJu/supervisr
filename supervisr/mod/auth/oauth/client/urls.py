"""
Supervisr auth oauth client urls
"""

from django.conf.urls import url

from supervisr.mod.auth.oauth.client.views import core
from supervisr.mod.auth.oauth.client.views.providers import (facebook, github,
                                                             supervisr,
                                                             twitter)

urlpatterns = [
    url(r'^callback/(?P<provider>supervisr)/$',
        supervisr.SupervisrOAuthCallback.as_view(), name='oauth-client-callback'),
    url(r'^callback/(?P<provider>twitter)/$',
        twitter.TwitterOAuthCallback.as_view(), name='oauth-client-callback'),
    url(r'^callback/(?P<provider>github)/$',
        github.GitHubOAuth2Callback.as_view(), name='oauth-client-callback'),
    url(r'^callback/(?P<provider>facebook)/$',
        facebook.FacebookOAuth2Callback.as_view(), name='oauth-client-callback'),
    url(r'^login/(?P<provider>facebook)/$',
        facebook.FacebookOAuthRedirect.as_view(), name='oauth-client-login'),

    url(r'^login/(?P<provider>(\w|-)+)/$', core.OAuthRedirect.as_view(),
        name='oauth-client-login'),
    url(r'^callback/(?P<provider>(\w|-)+)/$', core.OAuthCallback.as_view(),
        name='oauth-client-callback'),
]
