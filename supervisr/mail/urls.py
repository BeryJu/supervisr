"""
Supervisr Mail URLs
"""

from django.conf.urls import url

from .views import mail

urlpatterns = [
    url(r'^$', mail.index, name='mail-index'),
    url(r'^accounts/new/$', mail.AccountNewView.as_view(), name='mail-account-new'),
    url(r'^(?P<account>[a-zA-Z0-9\-\.]+)\@(?P<domain>[a-z0-9\-\.]+)/$',
        mail.accounts_view, name='mail-account-view'),
    url(r'^(?P<account>[a-zA-Z0-9\-\.]+)\@(?P<domain>[a-z0-9\-\.]+)/edit/$',
        mail.account_edit, name='mail-account-edit'),
    url(r'^(?P<account>[a-zA-Z0-9\-\.]+)\@(?P<domain>[a-z0-9\-\.]+)/delete/$',
        mail.account_delete, name='mail-account-delete'),
]
