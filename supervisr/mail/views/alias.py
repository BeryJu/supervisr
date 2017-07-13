"""
Supervisr Mail Alias Views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext as _

from supervisr.mail.models import MailDomain, MailForwarder


@login_required
def index(req):
    """
    Index of aliases
    """
    domains = MailDomain.objects.filter(users__in=[req.user])
    fwd_accounts = MailForwarder.objects \
        .filter(account__domain__in=domains, account__users__in=[req.user]) \
        .order_by('account__domain', 'account__address')
    paginator = Paginator(fwd_accounts, int(req.GET.get('per_page', 50)))

    page = req.GET.get('page')
    try:
        aliases = paginator.page(page)
    except PageNotAnInteger:
        aliases = paginator.page(1)
    except EmptyPage:
        aliases = paginator.page(paginator.num_pages)

    return render(req, 'mail/alias/index.html', {
        'fwd_accounts': aliases,
        })

@login_required
# pylint: disable=unused-argument
def forwarder_delete(req, domain, dest):
    """
    Show view to delete account
    """
    domains = MailDomain.objects.filter(domain__domain=domain)
    if not domains.exists():
        raise Http404
    r_domain = domains.first()

    fwds = MailForwarder.objects.filter(account__domain=r_domain, destination=dest)
    if not fwds.exists():
        raise Http404
    r_fwd = fwds.first()

    if req.method == 'POST' and 'confirmdelete' in req.POST:
        # User confirmed deletion
        r_fwd.delete()
        messages.success(req, _('Forwarder successfully deleted'))
        return redirect(reverse('supervisr/mail:mail-index'))

    return render(req, 'core/generic_delete.html', {
        'object': 'Forwarder %s' % r_fwd.destination,
        'delete_url': reverse('supervisr/mail:mail-alias-delete', kwargs={
            'domain': r_domain.domain.domain,
            'dest': r_fwd.destination
            })
        })
