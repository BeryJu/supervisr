"""
Supervisr Web Provider
"""

from django.utils.translation import ugettext as _

from supervisr.core.providers.base import BaseProvider, ProviderMetadata


class BaseWebProvider(BaseProvider):
    """
    Base Class for all Web Providers
    """

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
            super(BaseWebProvider.Meta, self).__init__(provider)
            self.selectable = False
            self.ui_name = _('BaseWebProvider')
