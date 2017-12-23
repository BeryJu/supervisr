"""Supervisr Core Middleware to authenticate via API Key"""

from django.core.exceptions import ValidationError

from supervisr.core.api.utils import api_response
from supervisr.core.models import SVAnonymousUser, User


def api_key_auth(get_response):
    """Middleware to authenticate via API Key"""

    def middleware(req):
        """Middleware to authenticate via API Key"""
        if isinstance(req.user, SVAnonymousUser):
            key = SVAnonymousUser.api_key
            key_name = 'sv-api-key'
            if key_name in req.GET:
                key = req.GET.get(key_name)
            elif key_name in req.POST:
                key = req.POST.get(key_name)
            elif key_name in req.META:
                key = req.META.get(key_name)

            users = User.objects.filter(api_key=key, is_active=True)
            try:
                if not users.exists() and key != SVAnonymousUser.api_key:
                    return api_response(req, {'error': "Invalid API Key", 'code': 400})
                elif users.exists():
                    req.user = users.first()
            except ValidationError: # Invalid UUID
                pass
        response = get_response(req)
        return response
    return middleware
