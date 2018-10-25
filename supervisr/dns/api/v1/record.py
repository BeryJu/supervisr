"""Supervisr DNS v1 Record API"""
from django.http import HttpRequest, HttpResponse

from supervisr.core.api.models import UserAcquirableModelAPI
from supervisr.core.decorators import logged_in_or_basicauth
from supervisr.core.utils import get_remote_ip
from supervisr.dns.api.utils import BadAuthResponse, GoodResponse
from supervisr.dns.forms.records import DataRecordForm, SetRecordForm
from supervisr.dns.models import DataRecord, SetRecord


class DataRecordAPI(UserAcquirableModelAPI):
    """Record API"""

    model = DataRecord
    form = DataRecordForm


class SetRecordAPI(UserAcquirableModelAPI):
    """Record API"""

    model = SetRecord
    form = SetRecordForm


@logged_in_or_basicauth('Supervisr DNS Update')
def dyndns_update(request: HttpRequest, record_uuid: str) -> HttpResponse:
    """Update DNS entry, but with basic auth"""
    records = DataRecord.objects.filter(uuid=record_uuid, users__in=[request.user])
    if not records.exists():
        return BadAuthResponse()

    record = records.first()
    record.content = get_remote_ip(request)
    record.save()

    return GoodResponse()
