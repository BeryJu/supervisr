"""
Supervisr Server URLs
"""

from django.conf.urls import url

from .views import server

urlpatterns = [
    url(r'^$', server.index, name='server-index'),
]
