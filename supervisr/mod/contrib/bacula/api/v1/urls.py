"""
Supervisr Bacula v1 API Urls
"""

from django.conf.urls import url

from supervisr.mod.contrib.bacula.api.v1.graphs import GraphAPI

urlpatterns = [
    url(r'^graph/(?P<verb>\w+)/$', GraphAPI.as_view(), name='graph'),
]
