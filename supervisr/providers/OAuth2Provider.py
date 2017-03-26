"""
Supervisr Core OAuth2 Provider
"""

# from django.contrib.auth.models import Group
from .BaseProvider import BaseProvider


class OAuth2Provider(BaseProvider):
    """
    Base Class for Providers that use OAuth2 to authenticate users
    """

    name = 'OAuth2Provider'
    managed_by = []
