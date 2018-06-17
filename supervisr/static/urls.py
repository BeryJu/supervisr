"""Supervisr Static URLs"""
from django.conf.urls import url
from supervisr.static import views

urlpatterns = [
    url(r'^feed/', views.FeedView.as_view(), name='page-feed'),
    url(r'^page/(?P<slug>[-\w]+)/$',
        views.PageView.as_view(), name='page-view'),
    url(r'^page/(?P<slug>[-\w]+)/(?P<lang>[a-z\-]{2,7})/$',
        views.PageView.as_view(), name='page-view'),
]
