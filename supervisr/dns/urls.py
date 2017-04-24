"""
Supervisr DNS URLs
"""

from django.conf.urls import url

from .views import dns

urlpatterns = [
    url(r'^$', dns.index, name='dns-index'),
]
