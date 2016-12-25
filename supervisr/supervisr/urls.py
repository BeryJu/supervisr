from django.conf.urls import url
from django.contrib import admin
from .views import common
from .views import account

urlpatterns = [
    url(r'^$', common.index, name='common-index'),
    url(r'^accounts/login/$', account.login, name='account-login'),
    url(r'^accounts/signup/$', account.signup, name='account-signup'),
    url(r'^accounts/logout/$', account.logout, name='account-logout'),
    url(r'^accounts/change_password/$', account.change_password, name='account-change_password'),
    url(r'^admin/', admin.site.urls),
]
