"""Supervisr PowerDNS Domain Provider"""
from logging import getLogger

from supervisr.core.providers.base import ProviderObjectTranslator
from supervisr.dns.models import ReverseZone, Zone
from supervisr.dns.providers.compat import CompatDNSProvider, CompatDNSRecord
from supervisr.provider.nix_dns.providers.translators.record import \
    PowerDNSRecordTranslator
from supervisr.provider.nix_dns.providers.translators.zone import \
    PowerDNSZoneTranslator

LOGGER = getLogger(__name__)

class NixDNSProvider(CompatDNSProvider):
    """PowerDNS provider"""

    parent = None

    def get_translator(self, data_type) -> ProviderObjectTranslator:
        if data_type in [Zone, ReverseZone]:
            return PowerDNSZoneTranslator
        if data_type == CompatDNSRecord:
            return PowerDNSRecordTranslator
        # DataRecord and SetRecord is handeled by Compat
        return super().get_translator(data_type)

    def check_credentials(self, credentials=None):
        return self.parent.check_credentials(credentials)

    def check_status(self):
        return self.parent.check_status()
