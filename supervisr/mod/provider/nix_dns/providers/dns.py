"""Supervisr PowerDNS Domain Provider"""

from supervisr.core.providers.base import ProviderObjectTranslator
from supervisr.dns.models import Zone
from supervisr.dns.providers.base import BaseDNSProvider
from supervisr.mod.provider.nix_dns.providers.translators.zone import \
    PowerDNSZoneTranslator


class PowerDNSDBDNSProvider(BaseDNSProvider):
    """PowerDNS provider"""

    parent = None

    def get_translator(self, data_type) -> ProviderObjectTranslator:
        if data_type == Zone:
            return PowerDNSZoneTranslator
        return None

    def check_credentials(self, credentials=None):
        """
        Check if Credentials is the correct class and try authentication.
        credentials might be none, in which case credentials from the constructor should be used.
        Should return False if check fails, otherwise True
        """
        return self.parent.check_credentials(credentials)

    def check_status(self):
        """
        This is used to check if the provider is reachable
        Expected Return values:
         - True: Everything is ok
         - False: Error (show generic warning)
         - String: Error (show string)
        """
        return self.parent.check_status()