from django.conf.urls import url
from django.contrib import admin
from .views import common
from .views import account

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', common.index),
    url(r'^accounts/login/$', account.login),
]
