"""
Supervisr OnlineNet Provider
"""

import requests
from django.core.exceptions import ValidationError
from slumber import API
from slumber.exceptions import HttpClientError

from supervisr.core.models import APIKeyCredential
from supervisr.core.providers.base import BaseProvider
from supervisr.mod.provider.onlinenet.providers.domain import \
    OnlineNetDomainProvider


# pylint: disable=too-few-public-methods
class OnlineNetProvider(BaseProvider):
    """
    OnlineNet provider
    """
    ui_name = "Online.net"
    api = None
    domain_provider = OnlineNetDomainProvider

    def __init__(self, credentials):
        super(OnlineNetProvider, self).__init__(credentials)
        self._init_api(self.credentials)

    def _init_api(self, cred):
        api_session = requests.session()
        api_session.headers['Authorization'] = 'Bearer %s' % cred.api_key
        self.api = API('https://api.online.net/api/v1', session=api_session)

    def check_credentials(self, credentials=None):
        """
        Check if credentials are instance of APIKeyCredential
        """
        if not credentials:
            credentials = self.credentials
        if not isinstance(credentials, APIKeyCredential):
            raise ValidationError("Credentials must be of Type 'API Key'")
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
        except HttpClientError as exc:
            return str(exc)
