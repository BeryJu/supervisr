"""Supervisr OnlineNet Provider"""

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from supervisr.core.models import EmptyCredential
from supervisr.core.providers.base import BaseProvider, ProviderMetadata
from supervisr.core.utils import check_db_connection
from supervisr.mod.provider.nix_dns.providers.dns import PowerDNSDBDNSProvider


# pylint: disable=too-few-public-methods
class PowerDNSDBProvider(BaseProvider):
    """PowerDNS DB Provider"""

    api = None

    def check_credentials(self, credentials: EmptyCredential = None):
        """Check if credentials are instance of BaseCredential"""
        return True

    def check_status(self):
        """Check connection status"""
        for name in ['powerdns', 'pdns', 'dns', 'default']:
            if name in settings.DATABASES:
                return check_db_connection(name)
        return False

    def get_provider(self, data_type) -> BaseProvider:
        if data_type._meta.app_label == 'supervisr_dns':
            return PowerDNSDBDNSProvider
        return None

    class Meta(ProviderMetadata):
        """PowerDNS core provider meta"""

        ui_description = _('Provides DNS hosted by a PowerDNS Server')
        ui_name = _('PowerDNS')
        capabilities = ['dns']
