"""Supervisr Mod Stats Influx"""

from django.conf.urls import url

from supervisr.mod.stats.influx import views

urlpatterns = [
    url(r'^settings/$', views.SettingsView.as_view(), name='admin_settings'),
]
