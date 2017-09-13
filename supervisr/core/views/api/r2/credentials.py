"""
Supervisr Core r2 Credential API
"""

from supervisr.core.forms.providers import (InternalCredentialForm,
                                            NewCredentialAPIForm,
                                            NewCredentialUserPasswordForm,
                                            NewCredentialUserPasswordServerForm)
from supervisr.core.models import BaseCredential
from supervisr.core.views.api.models import ProductAPI


class CredentialAPI(ProductAPI):
    """
    Credential API
    """
    model = BaseCredential
    form = [InternalCredentialForm,
            NewCredentialAPIForm,
            NewCredentialUserPasswordForm,
            NewCredentialUserPasswordServerForm]
