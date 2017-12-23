"""
Oauth2 Client Settings
"""

AUTHENTICATION_BACKENDS = [
    'supervisr.mod.auth.oauth.client.backends.AuthorizedServiceBackend',
]
