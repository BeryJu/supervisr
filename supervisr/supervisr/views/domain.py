"""
Supervisr Core Domain Views
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..models import Domain


@login_required
def index(req):
    """
    Show a n overview over all domains
    """
    user_domains = Domain.objects.filter(
        users__in=[req.user])
    return render(req, 'domain/index.html', {'domains': user_domains})
