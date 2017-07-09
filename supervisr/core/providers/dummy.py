"""
Supervisr Dummy Provider
"""

from supervisr.core.providers.base import BaseProvider
from supervisr.core.providers.domain import DomainProvider


class DummyBaseProvider(BaseProvider):
    """
    Dummy Provider which serves to test
    """

    selectable = True
    ui_name = 'Dummy Provider'

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
