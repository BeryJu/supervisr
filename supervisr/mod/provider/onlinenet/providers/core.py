"""
Supervisr OnlineNet Provider
"""

import requests
import slumber
from django.core.exceptions import ValidationError
from slumber.exceptions import HttpClientError

from supervisr.core.models import APIKeyCredential
from supervisr.core.providers.base import BaseProvider


# pylint: disable=too-few-public-methods
class OnlineNetProvider(BaseProvider):
    """
    OnlineNet provider
    """
    ui_name = "Online.net"
    api = None

    def __init__(self, credentials):
        super(OnlineNetProvider, self).__init__(credentials)
        self._init_api(self.credentials)

    def _init_api(self, cred):
        api_session = requests.session()
        api_session.headers['Authorization'] = 'Bearer %s' % cred.api_key
        self.api = slumber.API('https://api.online.net/api/v1', session=api_session)

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
        except HttpClientError as e:
            raise ValidationError("Invalid Credentials")

    def check_status(self):
        """
        Check connection status
        """
        try:
            self.api.user.info.get()
            return True
        except HttpClientError as e:
            return str(e)

    def test(self):
        pass
        # failovers = api.server.failover.get()
        # print(failovers)

        # # edit a failover IP
        # move_failover = api.server.failover.edit.post({
        #     'source': '10.0.0.42',
        #     'destination': '10.0.0.1'
        # })
        # print(move_failover)
