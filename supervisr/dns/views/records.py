"""
Supervisr DNS record views
"""
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from django.shortcuts import render

from supervisr.dns.models import Record, Zone


@login_required
def list_records(req, zone):
    """
    Show list of records for zone
    """
    # check if zone exists
    zones = Zone.objects.filter(domain__domain=zone, users__in=[req.user])
    if not zones.exists():
        raise Http404
    r_zone = zones.first()
    # get all records for the zone
    all_records = Record.objects.filter(domain=r_zone, users__in=[req.user]).order_by('name')

    paginator = Paginator(all_records, max(int(req.GET.get('per_page', 50)), 1))

    page = req.GET.get('page')
    try:
        records = paginator.page(page)
    except PageNotAnInteger:
        records = paginator.page(1)
    except EmptyPage:
        records = paginator.page(paginator.num_pages)

    return render(req, 'dns/records/index.html', {
        'records': records,
        'zone': r_zone,
        })
