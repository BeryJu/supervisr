"""
Supervisr OnlineNet Provider
"""

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from supervisr.core.providers.base import BaseProvider, ProviderMetadata
from supervisr.core.providers.internal import InternalCredential
from supervisr.core.utils import check_db_connection
from supervisr.mod.provider.powerdns.providers.dns import PowerDNSDBDNSProvider


# pylint: disable=too-few-public-methods
class PowerDNSDBProvider(BaseProvider):
    """
    PowerDNS DB Provider
    """
    api = None
    dns_provider = PowerDNSDBDNSProvider

    def check_credentials(self, credentials: InternalCredential = None):
        """
        Check if credentials are instance of BaseCredential
        """
        return True

    def check_status(self):
        """
        Check connection status
        """
        for name in ['powerdns', 'pdns', 'dns', 'default']:
            if name in settings.DATABASES:
                return check_db_connection(name)
        return False

    class Meta(ProviderMetadata):
        """
        PowerDNS core provider meta
        """

        def __init__(self, provider):
            super(PowerDNSDBProvider.Meta, self).__init__(provider)
            self.selectable = True
            self.ui_description = _('Provides DNS hosted by a PowerDNS Server')
            self.ui_name = _('PowerDNS')
