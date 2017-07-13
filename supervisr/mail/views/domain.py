"""
Supervisr Mail Domain Views
"""

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render

from supervisr.mail.models import MailDomain


@login_required
def view(req, domain):
    """
    Show details to a domain
    """
    domains = MailDomain.objects.filter(domain__domain=domain, users__in=[req.user])

    if not domains.exists():
        raise Http404
    r_domain = domains.first()

    return render(req, 'mail/domain/view.html', {
        'domain': r_domain,
        'title': '%s - Domains' % r_domain.domain.domain,
        })
