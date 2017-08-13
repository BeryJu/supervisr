"""
Supervisr DNS r1 Record API
"""

from supervisr.core.views.api.models import ProductAPI
from supervisr.dns.forms.records import RecordForm
from supervisr.dns.models import Record


class RecordAPI(ProductAPI):
    """
    Record API
    """
    model = Record
    form = RecordForm
