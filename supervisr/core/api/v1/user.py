"""
Supervisr Core APIv1
"""

# TODO: This import should not be hard-coded. It should dynamically be
# loaded when mod/auth/oauth/client is active.
from oauth2_provider.decorators import protected_resource

from supervisr.core.api.utils import api_response


@protected_resource()
def account_me(req):
    """
    Return oursevles as json
    """
    data = {}
    for field in ['pk', 'first_name', 'email']:
        data[field] = getattr(req.user, field)
    data['username'] = req.user.userprofile.username
    data['id'] = req.user.pk
    return api_response(req, data)
