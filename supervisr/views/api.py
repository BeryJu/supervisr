"""
Supervisr Core APIv1
"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


@login_required
def account_me(req):
    """
    Return oursevles as json
    """
    data = {}
    for field in ['pk', 'first_name', 'email']:
        data[field] = getattr(req.user, field)
    return JsonResponse(data)
