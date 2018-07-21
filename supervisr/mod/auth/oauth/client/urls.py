"""
Supervisr auth oauth client urls
"""

from django.conf.urls import url

from supervisr.mod.auth.oauth.client.views import core, settings
from supervisr.mod.auth.oauth.client.views.providers import (discord, facebook,
                                                             github, google,
                                                             reddit, supervisr,
                                                             twitter)

urlpatterns = [
    # Supervisr
    url(r'^callback/(?P<provider>supervisr)/$',
        supervisr.SupervisrOAuthCallback.as_view(), name='oauth-client-callback'),
    # Twitter
    url(r'^callback/(?P<provider>twitter)/$',
        twitter.TwitterOAuthCallback.as_view(), name='oauth-client-callback'),
    # GitHub
    url(r'^callback/(?P<provider>github)/$',
        github.GitHubOAuth2Callback.as_view(), name='oauth-client-callback'),
    # Facebook
    url(r'^callback/(?P<provider>facebook)/$',
        facebook.FacebookOAuth2Callback.as_view(), name='oauth-client-callback'),
    url(r'^login/(?P<provider>facebook)/$',
        facebook.FacebookOAuthRedirect.as_view(), name='oauth-client-login'),
    # Discord
    url(r'^callback/(?P<provider>discord)/$',
        discord.DiscordOAuth2Callback.as_view(), name='oauth-client-callback'),
    url(r'^login/(?P<provider>discord)/$',
        discord.DiscordOAuthRedirect.as_view(), name='oauth-client-login'),
    # Reddit
    url(r'^callback/(?P<provider>reddit)/$',
        reddit.RedditOAuth2Callback.as_view(), name='oauth-client-callback'),
    url(r'^login/(?P<provider>reddit)/$',
        reddit.RedditOAuthRedirect.as_view(), name='oauth-client-login'),
    # Google
    url(r'^callback/(?P<provider>google)/$',
        google.GoogleOAuth2Callback.as_view(), name='oauth-client-callback'),
    url(r'^login/(?P<provider>google)/$',
        google.GoogleOAuthRedirect.as_view(), name='oauth-client-login'),


    url(r'^login/(?P<provider>(\w|-)+)/$', core.OAuthRedirect.as_view(),
        name='oauth-client-login'),
    url(r'^callback/(?P<provider>(\w|-)+)/$', core.OAuthCallback.as_view(),
        name='oauth-client-callback'),
    url(r'^disconnect/(?P<provider>(\w|-)+)/$', core.disconnect, name='oauth-client-disconnect'),
    url(r'^settings/user/$', settings.user_settings, name='user_settings'),
]
