"""
supervisr core urls
"""

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin as admin_django

from .views import about, account, admin, common, domain, product

# pylint: disable=invalid-name
handler404 = 'supervisr.views.common.uncaught_404'
# pylint: disable=invalid-name
handler500 = 'supervisr.views.common.uncaught_500'

urlpatterns = [
    url(r'^$', common.index, name='common-index'),
    url(r'^accounts/login/$', account.login, name='account-login'),
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
    url(r'^products/$', product.index, name='product-index'),
    url(r'^products/(?P<slug>[a-zA-Z0-9\-]+)/$', product.view, name='product-view'),
    url(r'^domain/$', domain.index, name='domain-index'),
    url(r'^dns/', include('supervisr_dns.urls', 'supervisr_dns')),
    url(r'^mail/', include('supervisr_mail.urls', 'supervisr_mail')),
    url(r'^server/', include('supervisr_server.urls', 'supervisr_server')),
    url(r'^web/', include('supervisr_web.urls', 'supervisr_web')),
    url(r'^admin/$', admin.index, name='admin-index'),
    url(r'^admin/settings/', admin.settings, name='admin-settings'),
    url(r'^about/info/', about.info, name='about-info'),
    url(r'^about/changelog/$', about.changelog, name='about-changelog'),
    # Include django-admin and
    url(r'^admin/django/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/django/', admin_django.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
