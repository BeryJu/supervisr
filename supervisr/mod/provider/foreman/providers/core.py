"""
Supervisr Foreman Provider
"""

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from slumber import API
from slumber.exceptions import HttpClientError

from supervisr.core.providers.base import BaseProvider, ProviderMetadata
from supervisr.mod.provider.foreman.models import UserPasswordServerCredential


# pylint: disable=too-few-public-methods
class ForemanProvider(BaseProvider):
    """
    Foreman provider
    """
    api = None

    def __init__(self, credentials=None):
        super(ForemanProvider, self).__init__(credentials)
        if credentials:
            self._init_api(self.credentials)

    def _init_api(self, cred):
        if not isinstance(cred, UserPasswordServerCredential):
            raise ValidationError("Credentials must be of Type 'UserPasswordServerCredential Key'")
        self.api = API(cred.server, auth=(cred.username, cred.password))

    def check_credentials(self, credentials=None):
        """
        Check if credentials are instance of UserPasswordServerCredential
        """
        if not credentials:
            credentials = self.credentials
        self._init_api(credentials)
        try:
            self.api.users.get()
            return True
        except HttpClientError:
            raise ValidationError("Invalid Credentials")

    def check_status(self):
        """
        Check connection status
        """
        try:
            self.api.users.get()
            return True
        except HttpClientError as exc:
            return str(exc)

    class Meta(ProviderMetadata):
        """
        Foreman core provider meta
        """

        def __init__(self, provider):
            super(ForemanProvider.Meta, self).__init__(provider)
            self.selectable = True
            self.ui_description = _('Provides services hosted by a Foreman Server')
            self.ui_name = _('Foreman')
