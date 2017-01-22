"""
Supervisr Mail URLs
"""

from django.conf.urls import url
from .views import common

urlpatterns = [
    url(r'^$', common.index, name='mail-index'),
]
