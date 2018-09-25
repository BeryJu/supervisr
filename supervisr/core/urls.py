"""supervisr core urls"""
import importlib
import logging

from django.conf import settings as django_settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin as admin_django
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from supervisr.core.utils import get_apps
from supervisr.core.utils.constants import (DOMAIN_REGEX, EMAIL_REGEX,
                                            MOD_REGEX, UUID_REGEX)
from supervisr.core.views import (accounts, admin, common, domains, products,
                                  search, settings, setup, users)
from supervisr.core.views.providers import actions, credentials, instances

LOGGER = logging.getLogger(__name__)

handler404 = common.Uncaught404View.as_view()
handler500 = common.Uncaught500View.as_view()

admin_django.site.index_title = _('Supervisr Admin')
admin_django.site.site_title = _('supervisr')
admin_django.site.login = RedirectView.as_view(pattern_name=django_settings.LOGIN_URL,
                                               permanent=True, query_string=True)
admin_django.site.logout = RedirectView.as_view(pattern_name='account-logout',
                                                permanent=True, query_string=True)

urlpatterns = [
    # Account views
    url(r'^$', common.IndexView.as_view(), name='common-index'),
    url(r'^search/$', search.SearchView.as_view(), name='search'),
    url(r'^accounts/login/$', accounts.LoginView.as_view(), name=django_settings.LOGIN_URL),
    url(r'^accounts/login/reauth/$', accounts.ReauthView.as_view(), name='account-reauth'),
    url(r'^accounts/signup/$', accounts.SignUpView.as_view(), name='account-signup'),
    url(r'^accounts/logout/$', accounts.LogoutView.as_view(), name='account-logout'),
    url(r'^accounts/email_missing/$', accounts.EmailMissingView.as_view(),
        name='accounts-email-missing'),
    url(r'^accounts/confirm/(?P<uuid>%s)/$' % UUID_REGEX,
        accounts.AccountConfirmationView.as_view(), name='account-confirm'),
    url(r'^accounts/confirm/resend/(?P<email>%s)/$' % EMAIL_REGEX,
        accounts.ConfirmationResendView.as_view(), name='account-confirmation_resend'),
    url(r'^accounts/password/change/$', accounts.ChangePasswordView.as_view(),
        name='account-change_password'),
    url(r'^accounts/password/reset/$', accounts.PasswordResetInitView.as_view(),
        name='account-reset_password_init'),
    url(r'^accounts/password/reset/(?P<uuid>%s)/$' % UUID_REGEX,
        accounts.PasswordResetFinishView.as_view(), name='account-reset_password_confirm'),
    # Product views
    url(r'^products/$', products.ProductIndexView.as_view(), name='product-index'),
    url(r'^products/new/$', products.ProductNewWizard.as_view(), name='products-new'),
    url(r'^products/(?P<slug>[a-zA-Z0-9\-]+)/$', products.view, name='product-view'),
    # Domain views
    url(r'^domains/$', domains.DomainIndexView.as_view(), name='domain-index'),
    url(r'^domains/new/$', domains.DomainNewView.as_view(), name='domain-new'),
    url(r'^domains/(?P<domain>%s)/edit/$' % DOMAIN_REGEX,
        domains.DomainEditView.as_view(), name='domain-edit'),
    url(r'^domains/(?P<domain>%s)/delete/$' % DOMAIN_REGEX,
        domains.DomainDeleteView.as_view(), name='domain-delete'),
    # Provider - Instances
    url(r'^providers/instances/$', instances.ProviderIndexView.as_view(), name='instance-index'),
    url(r'^providers/instances/new/$', instances.ProviderCreateView.as_view(),
        name='instance-new'),
    url(r'^providers/instances/(?P<uuid>%s)/edit/$' % UUID_REGEX,
        instances.ProviderUpdateView.as_view(), name='instance-edit'),
    url(r'^providers/instances/(?P<uuid>%s)/delete/$' % UUID_REGEX,
        instances.ProviderDeleteView.as_view(), name='instance-delete'),
    # Provider - Credentials
    url(r'^providers/credentials/$',
        credentials.CredentialIndexView.as_view(), name='credential-index'),
    url(r'^providers/credentials/new/$', credentials.CredentialNewView.as_view(),
        name='credential-new'),
    url(r'^providers/credentials/(?P<uuid>%s)/edit/$' % UUID_REGEX,
        credentials.CredentialUpdateView.as_view(), name='credential-edit'),
    url(r'^providers/credentials/(?P<uuid>%s)/delete/$' % UUID_REGEX,
        credentials.CredentialDeleteView.as_view(), name='credential-delete'),
    # Provider - Actions
    url(r'^providers/actions/$',
        actions.ProviderUpdateViewTest.as_view(), name='provider-action'),
    # User views
    url(r'^user/$', users.index, name='user-index'),
    url(r'^user/events/$', users.events, name='user-events'),
    url(r'^user/delete/$', users.UserDeleteView.as_view(), name='user-delete'),
    url(r'^user/feedback/send/$', users.send_feedback, name='user-send_feedback'),
    # Admin views
    url(r'^admin/$', admin.IndexView.as_view(), name='admin-index'),
    url(r'^admin/users/$', admin.UserIndexView.as_view(), name='admin-users'),
    url(r'^admin/debug/$', admin.DebugView.as_view(), name='admin-debug'),
    url(r'^admin/monitoring/flower/$', admin.FlowerView.as_view(), name='admin-flower'),
    url(r'^admin/monitoring/info/$', admin.InfoView.as_view(), name='admin-info'),
    url(r'^admin/monitoring/tasks/$', admin.TasksView.as_view(), name='admin-tasks'),
    url(r'^admin/monitoring/events/$', admin.EventView.as_view(), name='admin-events'),
    url(r'^admin/products/$', products.ProductAdminIndex.as_view(), name='admin-product_index'),
    # Setup
    url(r'^setup/(?P<step>.+)/$', setup.SetupWizard.as_view(url_name='setup'), name='setup'),
    # Settings
    url(r'^admin/settings/module/default/$', settings.ModuleDefaultView.as_view(),
        name='admin-module_default'),
    url(r'^admin/settings/(?P<namespace>%s)/$' % MOD_REGEX,
        settings.settings, name='admin-settings'),
    # Include django-admin
    url(r'^admin/django/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/django/', admin_django.site.urls),
    # General API Urls
    url(r'^api/core/', include('supervisr.core.api.urls')),
    # Robots.txt to stop 404s
    url(r'^robots\.txt', TemplateView.as_view(template_name='common/robots.txt')),
]


def get_patterns(mount_path, module, namespace=None):
    """Check if module exists and return an array with urlpatterns"""
    # Check every part of the module chain
    mod_parts = module.split('.')
    # Walk through module to check existence
    # i.e.
    # check supervisr
    # check supervisr.core
    # check supervisr.core.url
    for _count in range(len(mod_parts) - 1, 0, -1):
        path = '.'.join(mod_parts[:-_count])
        if not importlib.util.find_spec(path):
            LOGGER.debug("Didn't find module '%s', not importing URLs from it.", path)
            return []
    if importlib.util.find_spec(module) is not None:
        LOGGER.debug("Loaded %s (namespace=%s)", module, namespace)
        return [
            url(mount_path, include((module, namespace), namespace=namespace)),
        ]
    return []


# Load Urls for all sub apps
for app in get_apps():
    # API namespace is always generated automatically
    api_namespace = '_'.join(app.name.split('_') + ['api'])
    # remove `supervisr/` for mountpath and replace _ with /
    mount_path = app.label.replace('supervisr_', '').replace('_', '/')

    # Only add if module could be loaded
    urlpatterns += get_patterns(r"^app/%s/" % mount_path, "%s.urls" % app.name, app.label)
    urlpatterns += get_patterns(r"^api/app/%s/" % mount_path, "%s.api.urls" % app.name)

if django_settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(django_settings.MEDIA_URL, document_root=django_settings.MEDIA_ROOT)
