"""
Supervisr Core Domain APIv1
"""

from supervisr.core.api.models import ProductAPI
from supervisr.core.forms.domains import DomainForm
from supervisr.core.models import Domain


class DomainAPI(ProductAPI):
    """
    Domain API
    """
    model = Domain
    form = DomainForm
