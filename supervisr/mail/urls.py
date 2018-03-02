"""
Supervisr Mail URLs
"""

from django.conf.urls import url

from supervisr.core.regex import DOMAIN_REGEX
#EMAIL_ADDRESS_REGEX, EMAIL_REGEX
# from supervisr.mail.views import account, alias, core, domain
from supervisr.mail.views import domains

urlpatterns = [
    url(r'^$', domains.MailDomainIndexView.as_view(), name='index'),
    # url(r'^accounts/$', account.index, name='mail-account-index'),
    # url(r'^accounts/new/$', account.AccountNewView.as_view(), name='mail-account-new'),

    # url(r'^aliases/$', alias.index, name='mail-alias-index'),
    # url(r'^aliases/new/$', alias.AliasNewView.as_view(), name='mail-alias-new'),

    url(r'^domains/new/$',
        domains.MailDomainNewWizard.as_view(), name='domain-new'),
    url(r'^(?P<domain>%s)/$' % DOMAIN_REGEX,
        domains.MailDomainReadView.as_view(), name='domain-view'),
    # url(r'^(?P<domain>%s)/alias/(?P<dest>%s)/edit/$' % (DOMAIN_REGEX, EMAIL_REGEX),
    #     alias.MailAliasUpdateView.as_view(), name='mail-alias-edit'),
    # url(r'^(?P<domain>%s)/alias/(?P<dest>%s)/delete/$' % (DOMAIN_REGEX, EMAIL_REGEX),
    #     alias.MailAliasDeleteView.as_view(), name='mail-alias-delete'),

    # url(r'^(?P<domain>%s)/account/(?P<account>%s)/edit/$' % (DOMAIN_REGEX, EMAIL_ADDRESS_REGEX),
    #     account.account_edit, name='mail-account-edit'),
    # url(r'^(?P<domain>%s)/account/(?P<account>%s)/delete/$' % (DOMAIN_REGEX, EMAIL_ADDRESS_REGEX),
    #     account.account_delete, name='mail-account-delete'),
    # url(r'^(?P<domain>%s)/account/(?P<account>%s)/password/set/$' %
    #     (DOMAIN_REGEX, EMAIL_ADDRESS_REGEX),
    #     account.account_set_password, name='mail-account-set-password'),
]
