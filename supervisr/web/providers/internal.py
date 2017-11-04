"""
Supervisr Web Provider
"""

from django.utils.translation import ugettext_lazy as _

from supervisr.core.providers.base import ProviderMetadata
from supervisr.web.providers.base import BaseWebProvider


class InternalWebProvider(BaseWebProvider):
    """
    Provider for Internally managed mail.
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
            super(InternalWebProvider.Meta, self).__init__(provider)
            self.selectable = False
            self.ui_name = _('InternalWebProvider')
