"""
Supervisr SAML IDP URLs
"""
from django.conf.urls import url

from supervisr.core.regex import MOD_REGEX
from supervisr.mod.auth.saml.idp import views

urlpatterns = [
    url(r'^login/$', views.login_begin, name="saml_login_begin"),
    url(r'^login/process/$', views.login_process, name='saml_login_process'),
    url(r'^logout/$', views.logout, name="saml_logout"),
    url(r'^metadata/xml/$', views.descriptor, name='metadata_xml'),
    url(r'^settings/(?P<mod>%s)/$' % MOD_REGEX, views.admin_settings, name='admin_settings'),
]
