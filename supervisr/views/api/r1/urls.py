"""
Supervisr Core r1 API Urls
"""

from django.conf.urls import include, url

from .user import account_me, openid_userinfo

urlpatterns = [
    url(r'^account/me.json$', account_me, name='api-r1-user-account_me'),
    url(r'^openid/userinfo$', openid_userinfo, name='api-r1-user-openid_userinfo'),
]
