"""
Supervisr API Urls
"""

from django.conf.urls import include, url

urlpatterns = [
    url('r1/', include('supervisr.dns.views.api.r1.urls')),
]
