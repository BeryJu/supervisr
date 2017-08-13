"""
Supervisr DNS Provider
"""

from supervisr.dns.providers.base import BaseDNSProvider


class InternalDNSProvider(BaseDNSProvider):
    """
    Provider for Internally managed DNS.
    """

    name = 'InternalDNSProvider'

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
