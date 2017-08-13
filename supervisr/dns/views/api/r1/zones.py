"""
Supervisr DNS r1 Zone API
"""

from supervisr.core.views.api.models import ProductAPI
from supervisr.dns.forms.zones import ZoneForm
from supervisr.dns.models import Zone


class ZoneAPI(ProductAPI):
    """
    Zone API
    """

    model = Zone
    form = ZoneForm
