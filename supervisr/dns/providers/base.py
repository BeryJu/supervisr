"""
Supervisr DNS Provider
"""

from django.utils.translation import ugettext_lazy as _

from supervisr.core.providers.base import BaseProvider, ProviderMetadata


class BaseDNSProvider(BaseProvider):
    """
    Base Class for all DNS Providers
    """

    name = 'BaseDNSProvider'
    selectable = False

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

    class Meta(ProviderMetadata):

        def __init__(self, provider):
            super(BaseDNSProvider.Meta, self).__init__(provider)
            self.selectable = False
            self.ui_name = _('BaseDNSProvider')
