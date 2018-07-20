"""supervisr mod web_proxy urls"""
from django.conf.urls import url
from supervisr.core.regex import SLUG_REGEX
from supervisr.mod.web_proxy.views import Proxy

urlpatterns = [
    url(r'^(?P<slug>%s)/(?P<path>.*)' % SLUG_REGEX, Proxy.as_view(), name='proxy'),
]
