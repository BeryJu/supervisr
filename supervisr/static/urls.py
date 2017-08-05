"""
Supervisr Puppet URLs
"""
from django.conf.urls import url

from supervisr.static import views

urlpatterns = [
    url(r'^feed/', views.feed, name='page-feed'),
    url(r'^page/(?P<slug>[-\w]+)/$', views.view, name='page-view'),
    url(r'^page/(?P<slug>[-\w]+)/(?P<lang>[a-z\-]{2,7})/$', views.view, name='page-view'),
]
