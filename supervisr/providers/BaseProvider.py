"""
Supervisr Core Provider
"""

# from django.contrib.auth.models import Group


class BaseProvider(object):
    """
    Base Class for all Providers
    """

    name = 'BaseProvider'
    managed_by = []
