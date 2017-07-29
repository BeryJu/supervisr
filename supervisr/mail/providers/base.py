"""
Supervisr Mail Provider
"""

from supervisr.core.providers.base import BaseProvider


class BaseMailProvider(BaseProvider):
    """
    Base Class for all Mail Providers
    """

    name = 'BaseMailProvider'

    def create_account(self, address=None, **kwargs):
        raise NotImplementedError()

    def get_account(self, address=None, **kwargs):
        raise NotImplementedError()

    def update_account(self, address=None, **kwargs):
        raise NotImplementedError()

    def delete_account(self, address=None, **kwargs):
        raise NotImplementedError()

    def create_domain(self, domain=None, **kwargs):
        raise NotImplementedError()

    def get_domain(self, domain=None, **kwargs):
        raise NotImplementedError()

    def update_domain(self, domain=None, **kwargs):
        raise NotImplementedError()

    def delete_domain(self, domain=None, **kwargs):
        raise NotImplementedError()
