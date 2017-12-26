"""
Supervisr DNS record views
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from supervisr.dns.models import ResourceSet


@login_required
def rset_view(request, rset):
    """View and edit ResourceSet"""
    res_set = get_object_or_404(ResourceSet, pk=rset, users__in=[request.user])
    records = res_set.resource.filter(users__in=[request.user])

    return render(request, 'dns/resourcesets/view.html', {
        'rset': res_set,
        'records': records
    })
