"""
Supervisr Core r2 API Urls
"""

from django.conf.urls import url

from supervisr.core.views.api.r2 import core, user

urlpatterns = [
    url(r'^core/health', core.health, name='api-r2-core-health'),
    url(r'^account/me', user.account_me, name='api-r2-user-account_me'),
]
