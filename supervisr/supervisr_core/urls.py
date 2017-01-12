from django.conf.urls import url, include
from django.contrib import admin
from .views import about
from .views import common
from .views import account
from .views import product

handler404 = 'supervisr.views.common.uncaught_404'
handler500 = 'supervisr.views.common.uncaught_500'

urlpatterns = [
    url(r'^$', common.index, name='common-index'),
    url(r'^accounts/login/$', account.login, name='account-login'),
    url(r'^accounts/signup/$', account.signup, name='account-signup'),
    url(r'^accounts/logout/$', account.logout, name='account-logout'),
    url(r'^accounts/change_password/$', account.change_password, name='account-change_password'),
    url(r'^accounts/confirm/(?P<uuid>[a-z0-9\-]{36})/$', account.confirm, name='account-confirm'),
    url(r'^product(s?)/$', product.index, name='product-index'),
    url(r'^product/(?P<slug>[a-zA-Z0-9\-]+)/$', product.view, name='product-view'),
    url(r'^product/(?P<slug>[a-zA-Z0-9\-]+)/new/$', product.new, name='product-new'),
    url(r'^product/(?P<slug>[a-zA-Z0-9\-]+)/edit/$', product.edit, name='product-edit'),
    url(r'^about/changelog/$', about.changelog, name='about-changelog'),
    url(r'^admin_django/', admin.site.urls),
]
