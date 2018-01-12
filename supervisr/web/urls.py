"""
Supervisr Web URLs
"""

from django.conf.urls import url

from supervisr.web.views import web

urlpatterns = [
    url(r'^$', web.index, name='index'),
]
