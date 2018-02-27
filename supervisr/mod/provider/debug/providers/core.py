"""
Supervisr OnlineNet Provider
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from supervisr.core.models import BaseCredential
from supervisr.core.providers.base import BaseProvider, ProviderMetadata
from supervisr.mod.provider.debug.providers.dns import DebugDNSProvider
from supervisr.mod.provider.debug.providers.mail import DebugMailProvider


# pylint: disable=too-few-public-methods
class DebugProvider(BaseProvider):
    """
    Debug  Provider
    """
    api = None
    dns_provider = DebugDNSProvider
    mail_provider = DebugMailProvider

    def check_credentials(self, credentials=None):
        """
        Check if credentials are instance of BaseCredential
        """
        return True

    def check_status(self):
        """
        Check connection status
        """
        return True

    class Meta(ProviderMetadata):
        """
        Debug core provider meta
        """

        def __init__(self, provider):
            super(DebugProvider.Meta, self).__init__(provider)
            self.selectable = True
            self.ui_description = _('Provides absolutely nothing.')
            self.ui_name = _('Debug')
