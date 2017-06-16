"""
Supervisr Mod LDAP urls
"""

from django.conf.urls import url

from supervisr.mod.ldap import views

urlpatterns = [
    url(r'^settings/(?P<mod>[a-zA-Z0-9]+)/$', views.admin_settings, name='admin_settings'),
]
