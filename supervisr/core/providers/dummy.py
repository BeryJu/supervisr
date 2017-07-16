"""
Supervisr Dummy Provider
"""

from supervisr.core.decorators import ifapp
from supervisr.core.providers.base import BaseProvider
from supervisr.core.providers.domain import DomainProvider


class DummyDomainProvider(DomainProvider):
    """
    Dummy Domain Provider which serves to test
    """

    selectable = False
    ui_name = 'Dummy Domain Provider'

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

class DummyBaseProvider(BaseProvider):
    """
    Dummy Provider which serves to test
    """

    selectable = True
    ui_name = 'Dummy Provider'
    domain_provider = DummyDomainProvider

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

@ifapp('supervisr/mail')
def register_mail_internal():
    """
    if Mail app is installed, add Internal Mail Provider to dummy class
    """
    from supervisr.mail.providers.internal import InternalMailProvider
    setattr(DummyBaseProvider, 'mail_provider', InternalMailProvider)

register_mail_internal()
