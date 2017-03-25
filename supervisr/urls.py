"""
supervisr core urls
"""
import importlib
import logging

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin as admin_django

from .utils import get_apps
from .views import about, account, admin, api, common, domain, product, user

LOGGER = logging.getLogger(__name__)

# pylint: disable=invalid-name
handler404 = 'supervisr.views.common.uncaught_404'
# pylint: disable=invalid-name
handler500 = 'supervisr.views.common.uncaught_500'

urlpatterns = [
    # Account views
    url(r'^$', common.index, name='common-index'),
    url(r'^accounts/login/$', account.login, name='account-login'),
    url(r'^accounts/login/reauth/$', account.reauth, name='account-reauth'),
    url(r'^accounts/signup/$', account.signup, name='account-signup'),
    url(r'^accounts/logout/$', account.logout, name='account-logout'),
    url(r'^accounts/confirm/(?P<uuid>[a-z0-9\-]{36})/$', account.confirm, name='account-confirm'),
    url(r'^accounts/confirm/resend/(?P<email>[a-zA-Z0-9@\.]*)/$',
        account.confirmation_resend, name='account-confirmation_resend'),
    url(r'^accounts/password/change/$', account.change_password, name='account-change_password'),
    url(r'^accounts/password/reset/$', account.reset_password_init,
        name='account-reset_password_init'),
    url(r'^accounts/password/reset/(?P<uuid>[a-z0-9\-]{36})/$',
        account.reset_password_confirm, name='account-reset_password_confirm'),
    # Product views
    url(r'^products/$', product.index, name='product-index'),
    url(r'^products/(?P<slug>[a-zA-Z0-9\-]+)/$', product.view, name='product-view'),
    # Domain views
    url(r'^domains/$', domain.index, name='domain-index'),
    url(r'^domains/new/$', domain.DomainNewView.as_view(), name='domain-new'),
    # User views
    url(r'^user/$', user.index, name='user-index'),
    url(r'^user/events/$', user.events, name='user-events'),
    # Admin views
    url(r'^admin/$', admin.index, name='admin-index'),
    url(r'^admin/settings/$', admin.settings, name='admin-settings'),
    url(r'^admin/mod/default/(?P<mod>[a-zA-Z0-9]+)/$', admin.mod_default, name='admin-mod_default'),
    url(r'^admin/info/$', admin.info, name='admin-info'),
    url(r'^admin/events/$', admin.events, name='admin-events'),
    url(r'^about/changelog/$', about.changelog, name='about-changelog'),
    # Include django-admin
    url(r'^admin/django/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/django/', admin_django.site.urls),
    url(r'^api/oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^api/v1/account/me.json$', api.account_me, name='api-account_me'),
    url(r'^api/v1/openid/userinfo$', api.openid_userinfo, name='api-openid_userinfo'),
]

# Load Urls for all sub apps
for app in get_apps():
    short_name = app.replace('supervisr_', '').replace('_', '/')
    # Check if it's only a module or a full path
    if '.' in app:
        app = app.split('.')[0]
        short_name = short_name.split('.')[0]
    url_module = "%s.urls" % app
    # Only add if module could be loaded
    if importlib.util.find_spec(url_module) is not None:
        urlpatterns += [
            url(r"^app/%s/" % short_name, include(url_module, app)),
        ]
        LOGGER.info("Loaded %s", url_module)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
