"""Supervisr libcloud Domain Provider"""

from libcloud.dns.providers import get_driver

from supervisr.core.providers.base import ProviderObjectTranslator
from supervisr.dns.models import ReverseZone, Zone
from supervisr.dns.providers.compat import CompatDNSProvider, CompatDNSRecord
from supervisr.provider.libcloud.models import LibCloudCredentials
from supervisr.provider.libcloud.providers.translators.record import \
    LCloudRecordTranslator
from supervisr.provider.libcloud.providers.translators.zone import \
    LCloudZoneTranslator


class LibCloudDNSProvider(CompatDNSProvider):
    """libcloud DNS provider"""

    parent = None

    driver_cls = None
    driver = None

    def __init__(self, credentials: LibCloudCredentials):
        super().__init__(credentials)
        # Create new libcloud Provider instance
        self.driver_cls = get_driver(credentials.provider)
        self.driver = self.driver_cls(
            key=credentials.key,
            secret=credentials.secret,
            secure=credentials.secure,
            host=credentials.host,
            port=credentials.port,
            api_version=credentials.api_version,
            region=credentials.region,
        )

    def get_translator(self, data_type) -> ProviderObjectTranslator:
        if data_type in [Zone, ReverseZone]:
            return LCloudZoneTranslator
        if data_type == CompatDNSRecord:
            return LCloudRecordTranslator
        return super().get_translator(data_type)

    def check_credentials(self, credentials=None):
        """Check Credentials"""
        return self.parent.check_credentials(credentials)

    def check_status(self):
        """check provider status"""
        return self.parent.check_status()
