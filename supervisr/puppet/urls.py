"""
Supervisr Puppet URLs
"""
from django.conf.urls import url

from supervisr.puppet import views

urlpatterns = [
    url(r'v3/modules$', views.module_list, name='module-list'),
    url(r'v3/modules/(?P<user>[a-z0-9]+)-(?P<module>[a-z0-9_]+)$', views.module, name='module'),
    url(r'v3/users$', views.user_list, name='user-list'),
    url(r'v3/users/(?P<user>[a-z0-9]+)$', views.user, name='user'),
    url(r'v3/releases$', views.release_list, name='release-list'),
    url(r'v3/releases/(?P<user>[a-z0-9]+)-(?P<module>[a-z0-9_]+)-(?P<version>[a-z0-9\.]+)$',
        views.release, name='release'),
    url(r'v3/files/(?P<user>[a-z0-9]+)-(?P<module>[a-z0-9_]+)-(?P<version>[a-z0-9\.]+).tar.gz$',
        views.file, name='file'),
    url(r'debug/build/(?P<user>[a-z0-9]+)-(?P<module>[a-z0-9_]+)$',
        views.debug_build, name='debug-build'),
]
