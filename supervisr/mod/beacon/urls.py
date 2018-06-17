"""Supervisr Beacon URLs"""

from django.conf.urls import url
from supervisr.mod.beacon import views

urlpatterns = [
    url(r'^settings/$', views.admin_settings, name='admin_settings'),
    url(r'^pulse/$', views.pulse, name='pulse'),
]
