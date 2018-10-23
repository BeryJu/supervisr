"""Supervisr DNS v1 Zone API"""

from supervisr.core.api.models import UserAcquirableModelAPI
from supervisr.dns.forms.reverse_zones import ReverseZoneForm
from supervisr.dns.forms.zones import ZoneForm
from supervisr.dns.models import ReverseZone, Zone


class ZoneAPI(UserAcquirableModelAPI):
    """Zone API"""

    model = Zone
    form = ZoneForm


class ReverseZoneAPI(UserAcquirableModelAPI):
    """ReverseZone API"""

    model = ReverseZone
    form = ReverseZoneForm
