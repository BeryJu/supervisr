"""
Supervisr Mail Common Views
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from supervisr.mail.models import MailAccount, MailAlias, MailDomain


@login_required
def index(req):
    """
    Mail Domain Index
    """
    domains = MailDomain.objects.filter(users__in=[req.user])
    accounts = MailAccount.objects \
        .filter(domain__in=domains, users__in=[req.user]) \
        .order_by('domain', 'address')
    aliases = MailAlias.objects \
        .filter(account__domain__in=domains, account__users__in=[req.user]) \
        .order_by('account__domain', 'account__address')

    return render(req, 'mail/index.html', {
        'domains': domains,
        'accounts': accounts,
        'aliases': aliases,
        })
