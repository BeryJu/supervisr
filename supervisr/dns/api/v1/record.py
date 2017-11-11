"""
Supervisr DNS r1 Record API
"""
from django.http import HttpResponse

from supervisr.core.api.models import ProductAPI
from supervisr.core.decorators import logged_in_or_basicauth
from supervisr.core.utils import get_remote_ip
from supervisr.dns.forms.records import RecordForm
from supervisr.dns.models import Record, Zone


class RecordAPI(ProductAPI):
    """
    Record API
    """
    model = Record
    form = RecordForm

@logged_in_or_basicauth('Supervisr DNS Update')
def dyndns_update(req, zone, record):
    """
    Update DNS entry, but with basic auth
    """
    zones = Zone.objects.filter(domain__domain=zone, users__in=[req.user])
    if not zones.exists():
        return HttpResponse('bad auth')
    r_zone = zones.first()

    records = Record.objects.filter(domain=r_zone, name=record, type='A')
    if not records.exists():
        return HttpResponse('nohost')
    r_record = records.first()

    remote = get_remote_ip(req)
    if r_record.content == remote:
        return HttpResponse("nochg %s" % remote)

    r_record.content = remote
    r_record.save()
    return HttpResponse("ok")
