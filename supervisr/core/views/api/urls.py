"""
Supervisr API Urls
"""

from django.conf.urls import include, url

urlpatterns = [
    url('r1/', include('supervisr.core.views.api.r1.urls')),
    url('r2/', include('supervisr.core.views.api.r2.urls')),
]
