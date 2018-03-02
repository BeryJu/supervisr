"""Supervisr Internal Provider"""

from django.utils.translation import ugettext_lazy as _

from supervisr.core.models import BaseCredential
from supervisr.core.providers.base import BaseProvider, ProviderMetadata
from supervisr.core.providers.domain import DomainProvider


class InternalCredential(BaseCredential):
    """Internally used Credential"""

    form = 'supervisr.core.forms.providers.InternalCredentialForm'

    @staticmethod
    def type():
        """Return type"""
        return _('Internal Credential')

class InternalDomainProvider(DomainProvider):
    """Internal Domain Provider which serves to test"""

    def check_credentials(self, credentials=None):
        """Check if credentials are instance of APIKeyCredential"""
        return True

    def check_status(self):
        """Check connection status"""
        return True

    # pylint: disable=too-few-public-methods
    class Meta(ProviderMetadata):
        """Internal Domain Provider Meta"""

        selectable = False

        def __init__(self, provider):
            super(InternalDomainProvider.Meta, self).__init__(provider)
            self.ui_name = _('Internal Domain Provider')

class InternalBaseProvider(BaseProvider):
    """Internal Provider which serves to test"""

    domain_provider = InternalDomainProvider

    def check_credentials(self, credentials=None):
        """Check if credentials are instance of APIKeyCredential"""
        return True

    def check_status(self):
        """Check connection status"""
        return True

    # pylint: disable=too-few-public-methods
    class Meta(ProviderMetadata):
        """Internal Base Provider meta"""

        selectable = True

        def __init__(self, provider):
            super(InternalBaseProvider.Meta, self).__init__(provider)
            self.ui_description = _(
                'This Provider is used to provide service with Supervisr managed servers.')
            self.ui_name = _('Internal Provider')
