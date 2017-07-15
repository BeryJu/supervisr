"""
Supervisr Mail URLs
"""

from django.conf.urls import url

from supervisr.mail.views import account, alias, core, domain

ADDRESS_REGEX = r'[a-zA-Z0-9_.+-/]+'
DOMAIN_REGEX = r'[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
FULL_ADDRESS_REGEX = r'[a-zA-Z0-9_.+-/]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

urlpatterns = [
    url(r'^$', core.index, name='mail-index'),
    url(r'^accounts/$', account.index, name='mail-account-index'),
    url(r'^accounts/new/$', account.AccountNewView.as_view(), name='mail-account-new'),

    url(r'^aliases/$', alias.index, name='mail-alias-index'),
    url(r'^aliases/new/$', alias.AliasNewView.as_view(), name='mail-alias-new'),

    url(r'^(?P<domain>%s)/(?P<account>%s)/edit/$' % (DOMAIN_REGEX, ADDRESS_REGEX),
        account.account_edit, name='mail-account-edit'),
    url(r'^(?P<domain>%s)/(?P<account>%s)/delete/$' % (DOMAIN_REGEX, ADDRESS_REGEX),
        account.account_delete, name='mail-account-delete'),
    url(r'^(?P<domain>%s)/(?P<account>%s)/password/set/$' % (DOMAIN_REGEX, ADDRESS_REGEX),
        account.account_set_password, name='mail-account-set-password'),

    url(r'^(?P<domain>%s)/$' % DOMAIN_REGEX, domain.view, name='mail-domain-view'),
    url(r'^(?P<domain>%s)/(?P<dest>%s)/delete/$' % (DOMAIN_REGEX, FULL_ADDRESS_REGEX),
        alias.alias_delete, name='mail-alias-delete'),
]
