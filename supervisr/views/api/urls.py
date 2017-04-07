"""
Supervisr API Urls
"""

from django.conf.urls import include, url

urlpatterns = [
    url('r1/', include('supervisr.views.api.r1.urls')),
    url('r2/', include('supervisr.views.api.r2.urls')),
]
