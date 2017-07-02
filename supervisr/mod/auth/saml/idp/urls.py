"""
Supervisr SAML IDP URLs
"""
from django.conf.urls import url

from supervisr.mod.auth.saml.idp import views
from supervisr.mod.auth.saml.idp.metadata import get_deeplink_resources


def deeplink_url_patterns(
        prefix='',
        url_base_pattern=r'^%sinit/%s/$',
        login_init_func=views.login_init):
    """
    Returns new deeplink URLs based on 'links' from settings.SAML2IDP_REMOTES.
    Parameters:
    - url_base_pattern - Specify this if you need non-standard deeplink URLs.
        NOTE: This will probably closely match the 'login_init' URL.
    """
    resources = get_deeplink_resources()
    new_patterns = []
    for resource in resources:
        new_patterns += [
            url(url_base_pattern % (prefix, resource), login_init_func, {'resource': resource})
        ]
    return new_patterns

urlpatterns = [
    url(r'^login/$', views.login_begin, name="saml_login_begin"),
    url(r'^login/process/$', views.login_process, name='saml_login_process'),
    url(r'^logout/$', views.logout, name="saml_logout"),
    url(r'^metadata/xml/$', views.descriptor, name='metadata_xml'),
    # For "simple" deeplinks:
    url(r'^init/(?P<resource>\w+)/(?P<target>\w+)/$',
        views.login_init,
        name="login_init"),
    url(r'^settings/(?P<mod>[a-zA-Z0-9/]+)/$', views.admin_settings, name='admin_settings'),
]
# Issue 13 - Add new automagically-created URLs for deeplinks:
urlpatterns += deeplink_url_patterns()
