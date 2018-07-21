"""Supervisr Debug Provider"""

from django.utils.translation import ugettext_lazy as _
from supervisr.core.models import EmptyCredential
from supervisr.core.providers.base import (BaseProvider, ProviderMetadata,
                                           ProviderObjectTranslator)
from supervisr.mod.provider.debug.providers.dns import DebugDNSProvider
from supervisr.mod.provider.debug.providers.domain import DebugDomainProvider
from supervisr.mod.provider.debug.providers.mail import DebugMailProvider


class DebugProvider(BaseProvider):
    """Debug Provider"""

    api = None

    def check_credentials(self, credentials: EmptyCredential = None):
        """Check if credentials are instance of BaseCredential"""
        return True

    def get_translator(self, data_type) -> ProviderObjectTranslator:
        return None

    def get_provider(self, data_type) -> BaseProvider:
        if data_type._meta.app_label == 'supervisr_dns':
            return DebugDNSProvider
        elif data_type._meta.app_label == 'supervisr_mail':
            return DebugMailProvider
        elif data_type._meta.app_label == 'supervisr_core':
            return DebugDomainProvider
        return None

    def check_status(self):
        """Check connection status"""
        return True

    class Meta(ProviderMetadata):
        """Debug core provider meta"""

        ui_description = _('Provides absolutely nothing.')
        ui_name = _('Debug')
        capabilities = ['dns', 'mail', 'domain']
