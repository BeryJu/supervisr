from django.conf.urls import include, url
from django.contrib import admin

import supervisr_dns
import supervisr_mail
import supervisr_server
import supervisr_web

from .views import about, account, common, product

handler404 = 'supervisr.views.common.uncaught_404'
handler500 = 'supervisr.views.common.uncaught_500'

urlpatterns = [
    url(r'^$', common.index, name='common-index'),
    url(r'^accounts/login/$', account.login, name='account-login'),
    url(r'^accounts/signup/$', account.signup, name='account-signup'),
    url(r'^accounts/logout/$', account.logout, name='account-logout'),
    url(r'^accounts/change_password/$', account.change_password, name='account-change_password'),
    url(r'^accounts/confirm/(?P<uuid>[a-z0-9\-]{36})/$', account.confirm, name='account-confirm'),
    url(r'^products/$', product.index, name='product-index'),
    url(r'^products/(?P<slug>[a-zA-Z0-9\-]+)/$', product.view, name='product-view'),
    # url(r'^products/(?P<slug>[a-zA-Z0-9\-]+)/new/$', product.new, name='product-new'),
    # url(r'^products/(?P<slug>[a-zA-Z0-9\-]+)/edit/$', product.edit, name='product-edit'),
    url(r'^dns/', include('supervisr_dns.urls')),
    url(r'^mail/', include('supervisr_mail.urls')),
    url(r'^server/', include('supervisr_server.urls')),
    url(r'^web/', include('supervisr_web.urls')),
    url(r'^admin/django/jet/', include('jet.urls', 'jet')),
    url(r'^admin/django/jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    url(r'^admin/django/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/django/', admin.site.urls),
    url(r'^about/changelog/$', about.changelog, name='about-changelog'),
]
