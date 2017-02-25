"""
Supervisr Mail URLs
"""

from django.conf.urls import url

from .views import mail

urlpatterns = [
    url(r'^$', mail.index, name='mail-index'),
    url(r'^accounts/$', mail.accounts, name='mail-accounts'),
    # url(r'new/$', mail.new_step_1, name='mail-new'),
    url(r'(?P<domain>[a-z0-9\-]{36})/(?P<account>[a-z0-9\-]{36})/', mail.view, name='mail-view'),
]
