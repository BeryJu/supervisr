from django.conf.urls import url
from django.contrib import admin
from .views import common

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', common.index)
]
