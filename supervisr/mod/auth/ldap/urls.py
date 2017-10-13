"""
Supervisr Mod LDAP urls
"""

from django.conf.urls import url

from supervisr.core.regex import MOD_REGEX
from supervisr.mod.auth.ldap import views

urlpatterns = [
    url(r'^settings/(?P<mod>%s)/$' % MOD_REGEX, views.admin_settings, name='admin_settings'),
]
