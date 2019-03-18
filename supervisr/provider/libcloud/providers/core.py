"""Supervisr libcloud Provider"""

from django.utils.translation import ugettext_lazy as _

from supervisr.core.providers.base import BaseProvider, ProviderMetadata
from supervisr.provider.libcloud.models import LibCloudCredentials
from supervisr.provider.libcloud.providers.dns import LibCloudDNSProvider


class LibCloudProvider(BaseProvider):
    """LibCloud Provider"""

    def check_credentials(self, credentials: LibCloudCredentials = None):
        """Check if credentials are instance of BaseCredential"""
        # TODO: This should be delegated to
        return True

    def check_status(self):
        """Check connection status"""
        # TODO: Check status with libcloud?
        return True

    def get_provider(self, data_type) -> BaseProvider:
        if data_type._meta.app_label == 'supervisr_dns':
            return LibCloudDNSProvider
        return None

    class Meta(ProviderMetadata):
        """LibCloud core provider meta"""

        ui_description = _('Provides DNS hosted by any libcloud provider.')
        ui_name = _('libcloud')
        capabilities = ['dns']
