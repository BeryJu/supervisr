"""
Supervisr Mail URLs
"""

from django.conf.urls import url

from supervisr.mail.views import account, alias, core, domain

EMAIL_ADDRESS_REGEX = r'[a-zA-Z0-9_.+-/]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

urlpatterns = [
    url(r'^$', core.index, name='mail-index'),
    url(r'^accounts/$', account.index, name='mail-account-index'),
    url(r'^accounts/new/$', account.AccountNewView.as_view(), name='mail-account-new'),
    url(r'^(?P<domain>[a-z0-9\-\.]+)/(?P<account>[a-zA-Z0-9\-\.]+)/edit/$',
        account.account_edit, name='mail-account-edit'),
    url(r'^(?P<domain>[a-z0-9\-\.]+)/(?P<account>[a-zA-Z0-9\-\.]+)/delete/$',
        account.account_delete, name='mail-account-delete'),
    url(r'^aliases/$', alias.index, name='mail-alias-index'),
    url(r'^(?P<domain>[a-z0-9\-\.]+)/$', domain.view, name='mail-domain-view'),
    url(r'^(?P<domain>[a-z0-9\-\.]+)/(?P<dest>%s)/delete/$' % EMAIL_ADDRESS_REGEX,
        alias.forwarder_delete, name='mail-alias-delete'),
]
