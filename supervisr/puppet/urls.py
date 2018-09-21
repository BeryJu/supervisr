"""Supervisr Puppet URLs"""

from django.conf.urls import url

from supervisr.puppet.views import admin

urlpatterns = [
    url(r'^admin/$', admin.index, name='index'),
    url(r'^admin/debug/render/$', admin.debug_render, name='puppet-debug-render'),
    url(r'^admin/debug/build/(?P<user>[a-z0-9]+)-(?P<module>[a-z0-9_]+)$',
        admin.debug_build, name='puppet-debug-build'),
]
