"""Supervisr DNS v1 Zone API"""

from supervisr.core.api.models import UserAcquirableModelAPI
from supervisr.dns.forms.zones import ZoneForm
from supervisr.dns.models import Zone


class ZoneAPI(UserAcquirableModelAPI):
    """Zone API"""

    model = Zone
    form = ZoneForm
