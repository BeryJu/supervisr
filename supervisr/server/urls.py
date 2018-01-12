"""
Supervisr Server URLs
"""

from django.conf.urls import url

from supervisr.server.views import server

urlpatterns = [
    url(r'^$', server.index, name='index'),
]
