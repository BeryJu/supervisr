"""
Supervisr Internal Provider
"""

from django.utils.translation import ugettext_lazy as _

from supervisr.core.decorators import ifapp
from supervisr.core.models import BaseCredential
from supervisr.core.providers.base import BaseProvider, ProviderMetadata
from supervisr.core.providers.domain import DomainProvider


class InternalCredential(BaseCredential):
    """
    Internally used Credential
    """

    form = 'supervisr.core.forms.provider.InternalCredentialForm'

    @staticmethod
    def type():
        """
        Return type
        """
        return _('Internal Credential')

class InternalDomainProvider(DomainProvider):
    """
    Internal Domain Provider which serves to test
    """

    def check_credentials(self, credentials=None):
        """
        Check if credentials are instance of APIKeyCredential
        """
        return True

    def check_status(self):
        """
        Check connection status
        """
        return True

    # pylint: disable=too-few-public-methods
    class Meta(ProviderMetadata):
        """
        Internal Domain Provider Meta
        """

        selectable = False

        def __init__(self, provider):
            super(InternalDomainProvider.Meta, self).__init__(provider)
            self.ui_name = _('Internal Domain Provider')

class InternalBaseProvider(BaseProvider):
    """
    Internal Provider which serves to test
    """

    domain_provider = InternalDomainProvider

    def check_credentials(self, credentials=None):
        """
        Check if credentials are instance of APIKeyCredential
        """
        return True

    def check_status(self):
        """
        Check connection status
        """
        return True

    # pylint: disable=too-few-public-methods
    class Meta(ProviderMetadata):
        """
        Internal Base Provider meta
        """

        selectable = True

        def __init__(self, provider):
            super(InternalBaseProvider.Meta, self).__init__(provider)
            self.ui_description = _(
                'This Provider is used to provide service with Supervisr managed servers.')
            self.ui_name = _('Internal Provider')

@ifapp('supervisr/mail')
def register_mail_internal():
    """
    if Mail app is installed, add Internal Mail Provider to dummy class
    """
    from supervisr.mail.providers.internal import InternalMailProvider
    setattr(InternalBaseProvider, 'mail_provider', InternalMailProvider)

@ifapp('supervisr/dns')
def register_dns_internal():
    """
    if dns app is installed, add Internal dns Provider to dummy class
    """
    from supervisr.dns.providers.internal import InternalDNSProvider
    setattr(InternalBaseProvider, 'dns_provider', InternalDNSProvider)

register_mail_internal()
register_dns_internal()
