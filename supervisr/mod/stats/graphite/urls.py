"""
Supervisr Mod Stats Graphite
"""

from django.conf.urls import url

from supervisr.mod.stats.graphite import views

urlpatterns = [
    url(r'^settings/(?P<mod>[a-zA-Z0-9]+)/$', views.admin_settings, name='admin_settings'),
]
