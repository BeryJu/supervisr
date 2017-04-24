"""
Supervisr Mail Provider
"""

from .BaseMailProvider import BaseMailProvider


class InternalMailProvider(BaseMailProvider):
    """
    Provider for Internally managed mail.
    """

    name = 'InternalMailProvider'

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
