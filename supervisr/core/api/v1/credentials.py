"""Supervisr Core Credential APIv1"""

from supervisr.core.api.models import UserAcquirableModelAPI
from supervisr.core.forms.providers import (EmptyCredentialForm,
                                            NewCredentialAPIForm,
                                            NewCredentialUserPasswordForm,
                                            NewCredentialUserPasswordServerForm)
from supervisr.core.models import BaseCredential


class CredentialAPI(UserAcquirableModelAPI):
    """Credential API"""

    model = BaseCredential
    form = [EmptyCredentialForm,
            NewCredentialAPIForm,
            NewCredentialUserPasswordForm,
            NewCredentialUserPasswordServerForm]
