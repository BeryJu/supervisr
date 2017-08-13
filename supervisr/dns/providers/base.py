"""
Supervisr DNS Provider
"""

from supervisr.core.providers.base import BaseProvider


class BaseDNSProvider(BaseProvider):
    """
    Base Class for all DNS Providers
    """

    name = 'BaseDNSProvider'

    def create_account(self, address=None, **kwargs):
        raise NotImplementedError()

    def get_account(self, address=None, **kwargs):
        raise NotImplementedError()

    def update_account(self, address=None, **kwargs):
        raise NotImplementedError()

    def delete_account(self, address=None, **kwargs):
        raise NotImplementedError()

    def create_zone(self, zone=None, **kwargs):
        raise NotImplementedError()

    def get_zone(self, zone=None, **kwargs):
        raise NotImplementedError()

    def update_zone(self, zone=None, **kwargs):
        raise NotImplementedError()

    def delete_zone(self, zone=None, **kwargs):
        raise NotImplementedError()
