"""
Oauth2 Client Settings
"""
from django.conf import settings

AUTHENTICATION_BACKENDS = settings.AUTHENTICATION_BACKENDS + [
    'supervisr.mod.auth.oauth.client.backends.AuthorizedServiceBackend',
]
