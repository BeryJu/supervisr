"""
Supervisr Core Domain APIv1
"""

from supervisr.core.api.models import UserAcquirableModelAPI
from supervisr.core.forms.domains import DomainForm
from supervisr.core.models import Domain


class DomainAPI(UserAcquirableModelAPI):
    """
    Domain API
    """
    model = Domain
    form = DomainForm
