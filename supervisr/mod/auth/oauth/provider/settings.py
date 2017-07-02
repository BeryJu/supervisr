"""
Supervisr OAuth2 Provider
"""

CORS_ORIGIN_ALLOW_ALL = True
REQUEST_APPROVAL_PROMPT = 'auto'

MIDDLEWARE = [
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]
INSTALLED_APPS = [
    'oauth2_provider',
    'corsheaders',
]
