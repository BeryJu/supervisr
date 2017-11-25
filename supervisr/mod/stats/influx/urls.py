"""
Supervisr Mod Stats Influx
"""

from django.conf.urls import url

from supervisr.mod.stats.influx import views

urlpatterns = [
    url(r'^settings/$', views.admin_settings, name='admin_settings'),
]
