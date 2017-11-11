"""Supervisr mod beacon Pulse API"""

from supervisr.core.api.models import ModelAPI
from supervisr.mod.beacon.models import Pulse


class PulseAPI(ModelAPI):
    """Pulse API"""

    model = Pulse

    ALLOWED_VERBS = {
        'POST': ['create'],
    }

    # # pylint: disable=unused-argument
    # def create(self, request, data):
    #     """Create instance based on request data"""
    #     raise NotImplementedError()
