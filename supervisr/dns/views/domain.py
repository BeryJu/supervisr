"""
Supervisr DNS Views
"""

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render

from supervisr.core.models import Domain
from supervisr.dns.models import DNSDomain


@login_required
def index(req):
    """
    Show list of users domains
    """
    all_domains = Domain.objects.filter(users__in=[req.user])
    dns_domains = DNSDomain.objects.filter(domain__in=all_domains).order_by('domain__domain')

    paginator = Paginator(dns_domains, max(int(req.GET.get('per_page', 50)), 1))

    page = req.GET.get('page')
    try:
        domains = paginator.page(page)
    except PageNotAnInteger:
        domains = paginator.page(1)
    except EmptyPage:
        domains = paginator.page(paginator.num_pages)

    return render(req, 'dns/domain/index.html', {
        'domains': domains
        })
