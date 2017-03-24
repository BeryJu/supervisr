"""
Supervisr Mail URLs
"""

from django.conf.urls import url

from .views import mail

urlpatterns = [
    url(r'^$', mail.index, name='mail-index'),
    url(r'^accounts/$', mail.accounts, name='mail-accounts'),
    url(r'^accounts/new/$', mail.AccountNewView.as_view(), name='mail-account-new'),
    url(r'^domains/$', mail.index, name='mail-domains'),
    url(r'^domains/new/$', mail.DomainNewView.as_view(), name='mail-domain-new'),
    url(r'(?P<domain>[a-z0-9\-]{36})/(?P<account>[a-z0-9\-]{36})/',
        mail.accounts_view, name='mail-account-view'),
]
