"""
Supervisr Core r2 Provider API
"""

from supervisr.core.api.models import ProductAPI
from supervisr.core.forms.providers import ProviderForm
from supervisr.core.models import ProviderInstance
from supervisr.core.providers.base import get_providers


class ProviderAPI(ProductAPI):
    """
    Provider API
    """
    model = ProviderInstance
    form = ProviderForm

    def __init__(self, *args, **kwargs):
        super(ProviderAPI, self).__init__(*args, **kwargs)
        self.ALLOWED_VERBS['GET'].append('get_all')

    # pylint: disable=unused-argument, no-self-use
    def get_all(self, req, data):
        """
        Return list of all possible providers
        """
        return get_providers(path=True)
