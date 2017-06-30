"""
Supervisr Puppet URLs
"""
from django.conf.urls import url

from supervisr.puppet.views import admin, forge_api

urlpatterns = [
    url(r'^admin/$', admin.index, name='puppet-index'),
    url(r'^admin/debug/render/$', admin.debug_render, name='puppet-debug-render'),
    url(r'^admin/debug/build/(?P<user>[a-z0-9]+)-(?P<module>[a-z0-9_]+)$',
        admin.debug_build, name='puppet-debug-build'),

    url(r'^v3/modules$', forge_api.module_list, name='module-list'),
    url(r'^v3/modules/(?P<user>[a-z0-9]+)-(?P<module>[a-z0-9_]+)$', forge_api.module, name='module'),
    url(r'^v3/users$', forge_api.user_list, name='user-list'),
    url(r'^v3/users/(?P<user>[a-z0-9]+)$', forge_api.user, name='user'),
    url(r'^v3/releases$', forge_api.release_list, name='release-list'),
    url(r'^v3/releases/(?P<user>[a-z0-9]+)-(?P<module>[a-z0-9_]+)-(?P<version>[a-z0-9\.\+]+)$',
        forge_api.release, name='release'),
    url(r'^v3/files/(?P<user>[a-z0-9]+)-(?P<module>[a-z0-9_]+)-(?P<version>[a-z0-9\.\+]+).tar.gz$',
        forge_api.file, name='file'),
]
