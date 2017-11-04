"""
Supervisr Mail Provider
"""

from django.utils.translation import ugettext_lazy as _

from supervisr.core.providers.base import BaseProvider, ProviderMetadata


class BaseMailProvider(BaseProvider):
    """
    Base Class for all Mail Providers
    """

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

    class Meta(ProviderMetadata):

        def __init__(self, provider):
            super(BaseMailProvider.Meta, self).__init__(provider)
            self.selectable = False
            self.ui_name = _('BaseMailProvider')
