"""
Supervisr Puppet API v1 URLs
"""
from django.conf.urls import url

from supervisr.puppet.api.v1 import forge_api

urlpatterns = [
    url(r'^(?P<key>.{20})/v3/modules$', forge_api.module_list, name='module-list'),
    url(r'^(?P<key>.{20})/v3/modules/(?P<user>[a-z0-9]+)-(?P<module>[a-z0-9_]+)$',
        forge_api.module, name='module'),
    url(r'^(?P<key>.{20})/v3/users$', forge_api.user_list, name='user-list'),
    url(r'^(?P<key>.{20})/v3/users/'
        r'(?P<user>[a-z0-9]+)$', forge_api.user, name='user'),
    url(r'^(?P<key>.{20})/v3/releases$', forge_api.release_list, name='release-list'),
    url(r'^(?P<key>.{20})/v3/releases/(?P<user>[a-z0-9]+)-'
        r'(?P<module>[a-z0-9_]+)-(?P<version>[a-z0-9\.\+]+)$',
        forge_api.release, name='release'),
    url(r'^(?P<key>.{20})/v3/files/(?P<user>[a-z0-9]+)-(?P<module>[a-z0-9_]+)-'
        r'(?P<version>[a-z0-9\.\+]+).tar.gz$',
        forge_api.file, name='file'),
]
