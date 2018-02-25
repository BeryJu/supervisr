"""Supervisr DNS Provider"""

from django.utils.translation import ugettext_lazy as _

from supervisr.core.providers.base import BaseProvider, ProviderMetadata
from supervisr.core.providers.objects import ProviderObjectMarshall
from supervisr.dns.models import Record, Resource, Zone


class BaseDNSProvider(BaseProvider):
    """Base Class for all DNS Providers"""

    name = 'BaseDNSProvider'
    selectable = False
    zone_marshall = ProviderObjectMarshall[Zone]
    record_marshall = ProviderObjectMarshall[Record]
    resource_marshall = ProviderObjectMarshall[Resource]

    def check_credentials(self, credentials=None):
        """
        Check if Credentials is the correct class and try authentication.
        credentials might be none, in which case credentials from the constructor should be used.
        Should return False if check fails, otherwise True
        """
        raise NotImplementedError(
            "This Method should be overwritten by subclasses")

    def check_status(self):
        """
        This is used to check if the provider is reachable
        Expected Return values:
         - True: Everything is ok
         - False: Error (show generic warning)
         - String: Error (show string)
        """
        raise NotImplementedError(
            "This Method should be overwritten by subclasses")

    # pylint: disable=too-few-public-methods
    class Meta(ProviderMetadata):
        """Provider Meta"""

        def __init__(self, provider):
            super(BaseDNSProvider.Meta, self).__init__(provider)
            self.selectable = False
            self.ui_name = _('BaseDNSProvider')
