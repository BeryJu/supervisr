"""
Supervisr Core r2 API Urls
"""

from django.conf.urls import url

from .user import account_me

urlpatterns = [
    url(r'^account/me', account_me, name='api-r2-user-account_me'),
]
