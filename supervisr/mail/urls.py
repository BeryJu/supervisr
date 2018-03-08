"""
Supervisr Mail URLs
"""

from django.conf.urls import url

from supervisr.core.regex import DOMAIN_REGEX, EMAIL_ADDRESS_REGEX
#EMAIL_ADDRESS_REGEX, EMAIL_REGEX
# from supervisr.mail.views import account, alias, core, domain
from supervisr.mail.views import domains, addresses

urlpatterns = [
    url(r'^$', domains.MailDomainIndexView.as_view(), name='index'),

    url(r'^domains/new/$',
        domains.MailDomainNewWizard.as_view(), name='domain-new'),
    url(r'^domains/(?P<domain>%s)/$' % DOMAIN_REGEX,
        domains.MailDomainReadView.as_view(), name='domain-view'),
    url(r'^domains/(?P<domain>%s)/edit/$' % DOMAIN_REGEX,
        domains.MailDomainUpdateView.as_view(), name='domain-edit'),
    url(r'^domains/(?P<domain>%s)/delete/$' % DOMAIN_REGEX,
        domains.MailDomainDeleteView.as_view(), name='domain-delete'),

    url(r'^address/new/$',
        addresses.AddressNewWizard.as_view(), name='address-new'),
    url(r'^address/(?P<address>%s)(?P<pk>\d+)/$' % EMAIL_ADDRESS_REGEX,
        addresses.AddressReadView.as_view(), name='address-view'),
    url(r'^address/(?P<address>%s)(?P<pk>\d+)/edit/$' % EMAIL_ADDRESS_REGEX,
        addresses.AddressUpdateView.as_view(), name='address-edit'),
    url(r'^address/(?P<address>%s)(?P<pk>\d+)/delete/$' % EMAIL_ADDRESS_REGEX,
        addresses.AddressDeleteView.as_view(), name='address-delete'),

    # url(r'^(?P<domain>%s)/account/(?P<account>%s)/edit/$' % (DOMAIN_REGEX, EMAIL_ADDRESS_REGEX),
    #     account.account_edit, name='mail-account-edit'),
    # url(r'^(?P<domain>%s)/account/(?P<account>%s)/delete/$' % (DOMAIN_REGEX, EMAIL_ADDRESS_REGEX),
    #     account.account_delete, name='mail-account-delete'),
    # url(r'^(?P<domain>%s)/account/(?P<account>%s)/password/set/$' %
    #     (DOMAIN_REGEX, EMAIL_ADDRESS_REGEX),
    #     account.account_set_password, name='mail-account-set-password'),
]
