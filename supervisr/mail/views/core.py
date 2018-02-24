"""
Supervisr Mail Common Views
"""

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from supervisr.core.models import Domain
from supervisr.mail.models import MailDomain


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """Mail Domain Index"""
    all_domains = MailDomain.objects \
        .filter(users__in=[request.user]) \
        .order_by('domain__domain')
    unused_domains = Domain.objects.filter(users__in=[request.user]) \
        .exclude(pk__in=all_domains.values_list('domain', flat=True))
    domain_paginator = Paginator(all_domains, request.user.rows_per_page)
    page = request.GET.get('accountPage')
    try:
        domains = domain_paginator.page(page)
    except PageNotAnInteger:
        domains = domain_paginator.page(1)
    except EmptyPage:
        domains = domain_paginator.page(domain_paginator.num_pages)
    return render(request, 'mail/index.html', {
        'domains': domains,
        'unused_domains': unused_domains,
        })
