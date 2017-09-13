"""
Supervisr Core r2 Domain API
"""

from supervisr.core.forms.domains import DomainForm
from supervisr.core.models import Domain
from supervisr.core.views.api.models import ProductAPI


class DomainAPI(ProductAPI):
    """
    Domain API
    """
    model = Domain
    form = DomainForm
