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

@login_required
def openid_userinfo(req):
    """
    Return a OpenID Userinfo compatible endpoint
    """
    data = {}
    field_trans = {
        'sub': 'pk',
        'name': 'first_name',
        'email': 'email',
    }
    for new, orig in field_trans.items():
        data[new] = getattr(req.user, orig)
    return JsonResponse(data)
