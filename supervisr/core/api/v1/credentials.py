"""
Supervisr Core Credential APIv1
"""

from supervisr.core.api.models import UserAcquirableModelAPI
from supervisr.core.forms.providers import (InternalCredentialForm,
                                            NewCredentialAPIForm,
                                            NewCredentialUserPasswordForm,
                                            NewCredentialUserPasswordServerForm)
from supervisr.core.models import BaseCredential


class CredentialAPI(UserAcquirableModelAPI):
    """
    Credential API
    """
    model = BaseCredential
    form = [InternalCredentialForm,
            NewCredentialAPIForm,
            NewCredentialUserPasswordForm,
            NewCredentialUserPasswordServerForm]
