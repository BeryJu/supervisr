"""
Supervisr OnlineNet Provider
"""

import requests
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from slumber import API
from slumber.exceptions import HttpClientError

from supervisr.core.models import APIKeyCredential
from supervisr.core.providers.base import BaseProvider, ProviderMetadata
from supervisr.mod.provider.onlinenet.providers.domain import \
    OnlineNetDomainProvider


# pylint: disable=too-few-public-methods
class OnlineNetProvider(BaseProvider):
    """
    OnlineNet provider
    """
    api = None
    domain_provider = OnlineNetDomainProvider

    def __init__(self, credentials=None):
        super(OnlineNetProvider, self).__init__(credentials)
        if credentials:
            self._init_api(self.credentials)

    def _init_api(self, cred):
        if not isinstance(cred, APIKeyCredential):
            raise ValidationError("Credentials must be of Type 'API Key'")
        api_session = requests.session()
        api_session.headers['Authorization'] = 'Bearer %s' % cred.api_key
        self.api = API('https://api.online.net/api/v1', session=api_session)

    def check_credentials(self, credentials=None):
        """
        Check if credentials are instance of APIKeyCredential
        """
        if not credentials:
            credentials = self.credentials
        self._init_api(credentials)
        try:
            self.api.user.info.get()
            return True
        except HttpClientError:
            raise ValidationError("Invalid Credentials")

    def check_status(self):
        """
        Check connection status
        """
        try:
            self.api.user.info.get()
            return True
        except (HttpClientError, requests.exceptions.SSLError):
            return False

    class Meta(ProviderMetadata):
        """
        Online.net core provider meta
        """

        def __init__(self, provider):
            super(OnlineNetProvider.Meta, self).__init__(provider)
            self.selectable = True
            self.ui_description = _(
                'Provides services hosted by online.net')
            self.ui_name = _('Online.net')
