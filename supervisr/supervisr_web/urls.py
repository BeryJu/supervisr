"""
Supervisr Web URLs
"""

from django.conf.urls import url

from .views import web

urlpatterns = [
    url(r'^$', web.index, name='web-index'),
]
