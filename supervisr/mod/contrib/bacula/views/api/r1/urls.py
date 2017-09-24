"""
Supervisr Bacula r1 API Urls
"""

from django.conf.urls import url

from supervisr.mod.contrib.bacula.views.api.r1.graphs import GraphAPI

urlpatterns = [
    url(r'^graph/(?P<verb>\w+)/$', GraphAPI.as_view(), name='api-r1-graph'),
]
