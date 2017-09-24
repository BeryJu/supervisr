"""
Supervisr VMware Provider
"""

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from pyVim import connect

from supervisr.core.models import UserPasswordServerCredential
from supervisr.core.providers.base import BaseProvider, ProviderMetadata


# pylint: disable=too-few-public-methods
class VMwareProvider(BaseProvider):
    """
    VMware provider
    """
    service_instance = None

    def __init__(self, credentials=None):
        super(VMwareProvider, self).__init__(credentials)
        if credentials:
            self._init_api(self.credentials)

    def _init_api(self, cred):
        if not isinstance(cred, UserPasswordServerCredential):
            raise ValidationError("Credentials must be of Type 'UserPasswordServerCredential Key'")
        self.service_instance = connect.SmartConnectNoSSL(host=cred.server,
                                                          user=cred.username,
                                                          pwd=cred.password)

    def check_credentials(self, credentials=None):
        """
        Check if credentials are instance of UserPasswordServerCredential
        """
        if not credentials:
            credentials = self.credentials
        self._init_api(credentials)
        return True

    def check_status(self):
        """
        Check connection status
        """
        # self._init_api()
        return True

    class Meta(ProviderMetadata):
        """
        Foreman core provider meta
        """

        def __init__(self, provider):
            super(VMwareProvider.Meta, self).__init__(provider)
            self.selectable = True
            self.ui_description = _('Provides services hosted by a VMware vCenter')
            self.ui_name = _('VMware')
