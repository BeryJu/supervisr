"""
Supervisr Core APIv1
"""

from oauth2_provider.decorators import protected_resource

from ..utils import api_response


@protected_resource()
def account_me(req):
    """
    Return oursevles as json
    """
    data = {}
    for field in ['pk', 'first_name', 'email']:
        data[field] = getattr(req.user, field)
    data['id'] = req.user.pk
    return api_response(req, data)
