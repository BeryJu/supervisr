"""
supervisr core urls
"""
import importlib
import logging

from django.apps import apps
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin as admin_django
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from supervisr.core.regex import (DOMAIN_REGEX, EMAIL_REGEX, MOD_REGEX,
                                  UUID_REGEX)
from supervisr.core.utils import get_apps
from supervisr.core.views import (accounts, admin, common, domains, products,
                                  providers, search, users)

LOGGER = logging.getLogger(__name__)

# pylint: disable=invalid-name
handler404 = 'supervisr.core.views.common.uncaught_404'
# pylint: disable=invalid-name
handler500 = 'supervisr.core.views.common.uncaught_500'

admin_django.site.index_title = _('Supervisr Admin')
admin_django.site.site_title = _('supervisr')
admin_django.site.login = RedirectView.as_view(pattern_name=settings.LOGIN_URL,
                                               permanent=True, query_string=True)
admin_django.site.logout = RedirectView.as_view(pattern_name='account-logout',
                                                permanent=True, query_string=True)

urlpatterns = [
    # Account views
    url(r'^$', common.index, name='common-index'),
    url(r'^search/$', search.search, name='search'),
    url(r'^accounts/login/$', accounts.LoginView.as_view(), name=settings.LOGIN_URL),
    url(r'^accounts/login/reauth/$', accounts.reauth, name='account-reauth'),
    url(r'^accounts/signup/$', accounts.SignupView.as_view(), name='account-signup'),
    url(r'^accounts/logout/$', accounts.logout, name='account-logout'),
    url(r'^accounts/confirm/(?P<uuid>%s)/$' % UUID_REGEX, accounts.confirm, name='account-confirm'),
    url(r'^accounts/confirm/resend/(?P<email>%s)/$' % EMAIL_REGEX,
        accounts.confirmation_resend, name='account-confirmation_resend'),
    url(r'^accounts/password/change/$', accounts.change_password, name='account-change_password'),
    url(r'^accounts/password/reset/$', accounts.reset_password_init,
        name='account-reset_password_init'),
    url(r'^accounts/password/reset/(?P<uuid>%s)/$' % UUID_REGEX,
        accounts.reset_password_confirm, name='account-reset_password_confirm'),
    # Product views
    url(r'^products/$', products.index, name='product-index'),
    url(r'^products/new/$', products.ProductNewWizard.as_view(), name='products-new'),
    url(r'^products/(?P<slug>[a-zA-Z0-9\-]+)/$', products.view, name='product-view'),
    # Domain views
    url(r'^domains/$', domains.index, name='domain-index'),
    url(r'^domains/new/$', domains.DomainNewView.as_view(), name='domain-new'),
    url(r'^domains/(?P<domain>%s)/edit/$' % DOMAIN_REGEX, domains.edit, name='domain-edit'),
    url(r'^domains/(?P<domain>%s)/delete/$' % DOMAIN_REGEX, domains.delete, name='domain-delete'),
    # Provider
    url(r'^providers/instances/$', providers.instance_index, name='instance-index'),
    url(r'^providers/instances/new/$', providers.ProviderNewView.as_view(),
        name='instance-new'),
    url(r'^providers/instances/(?P<uuid>%s)/edit/$' % UUID_REGEX, providers.instance_edit,
        name='instance-edit'),
    url(r'^providers/instances/(?P<uuid>%s)/delete/$' % UUID_REGEX, providers.instance_delete,
        name='instance-delete'),
    # Credentials
    url(r'^providers/credentials/$', providers.credential_index, name='credential-index'),
    url(r'^providers/credentials/new/$', providers.CredentialNewView.as_view(),
        name='credential-new'),
    url(r'^providers/credentials/(?P<name>[a-zA-Z0-9\-\.\_\s]+)/delete/$',
        providers.credential_delete, name='credential-delete'),
    # User views
    url(r'^user/$', users.index, name='user-index'),
    url(r'^user/events/$', users.events, name='user-events'),
    url(r'^user/delete/$', users.UserDeleteView.as_view(), name='user-delete'),
    url(r'^user/feedback/send/$', users.send_feedback, name='user-send_feedback'),
    # Admin views
    url(r'^admin/$', admin.index, name='admin-index'),
    url(r'^admin/users/$', admin.users, name='admin-users'),
    url(r'^admin/settings/(?P<namespace>%s)/$' % MOD_REGEX,
        admin.settings, name='admin-settings'),
    url(r'^admin/mod/default/(?P<mod>%s)/$' % MOD_REGEX,
        admin.mod_default, name='admin-mod_default'),
    url(r'^admin/info/$', admin.info, name='admin-info'),
    url(r'^admin/events/$', admin.events, name='admin-events'),
    url(r'^admin/debug/$', admin.debug, name='admin-debug'),
    url(r'^admin/products/$', products.admin_index, name='admin-product_index'),
    # Include django-admin
    url(r'^admin/django/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/django/', admin_django.site.urls),
    # General API Urls
    url(r'^api/', include('supervisr.core.views.api.urls')),
    # Robots.txt to stop 404s
    url(r'^robots\.txt', TemplateView.as_view(template_name='common/robots.txt')),
]

# Load Urls for all sub apps
for app in get_apps():
    # Remove .apps.Supervisr stuff
    app = '.'.join(app.split('.')[:-2])
    # Check if app uses old or new label
    namespace = None
    # Try new format first
    # from supervisr.mod.auth.oauth.client
    # to mod/auth/oauth/client
    new_name = '/'.join(app.split('.'))
    mount_path = new_name.replace('supervisr/', '')
    app_config = apps.get_app_config(new_name)
    namespace = new_name

    url_module = "%s.urls" % app
    # Only add if module could be loaded
    if importlib.util.find_spec(url_module) is not None:
        urlpatterns += [
            url(r"^app/%s/" % mount_path, include(url_module, namespace=namespace)),
        ]
        LOGGER.info("Loaded %s (namespace=%s)", url_module, namespace)

if settings.DEBUG or settings.TEST:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
