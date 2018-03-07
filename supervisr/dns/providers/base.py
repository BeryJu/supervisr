"""Supervisr DNS Provider"""

from django.utils.translation import ugettext_lazy as _

from supervisr.core.providers.base import BaseProvider, ProviderMetadata


class BaseDNSProvider(BaseProvider):
    """Base Class for all DNS Providers"""

    name = 'BaseDNSProvider'
    selectable = False

    # pylint: disable=too-few-public-methods
    class Meta(ProviderMetadata):
        """Provider Meta"""

        def __init__(self, provider):
            super(BaseDNSProvider.Meta, self).__init__(provider)
            self.selectable = False
            self.ui_name = _('BaseDNSProvider')
