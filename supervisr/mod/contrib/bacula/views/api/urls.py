"""
Supervisr Bacula API Urls
"""

from django.conf.urls import include, url

urlpatterns = [
    url('r1/', include('supervisr.mod.contrib.bacula.views.api.r1.urls')),
]
