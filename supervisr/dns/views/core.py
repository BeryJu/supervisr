"""
Supervisr DNS Views
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from supervisr.core.models import Domain
from supervisr.dns.models import Record, Zone


@login_required
def index(req):
    """
    Show empty index page
    """
    domains = Zone.objects.filter(users__in=[req.user])
    unused_domains = Domain.objects.filter(users__in=[req.user]) \
        .exclude(pk__in=domains.values_list('domain', flat=True))

    records = Record.objects.filter(users__in=[req.user])
    zones = Zone.objects.filter(users__in=[req.user])

    return render(req, 'dns/index.html', {
        'unused_domains': unused_domains,
        'records': records,
        'zones': zones,
        })
