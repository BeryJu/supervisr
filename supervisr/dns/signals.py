"""
Supervisr DNS Signals
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from dns.exception import SyntaxError as DNSSyntaxError

from supervisr.core.signals import RobustSignal
from supervisr.dns.utils import rec_to_rd

LOGGER = logging.getLogger(__name__)

SIG_DNS_ZONE_UPDATE = RobustSignal(providing_args=['zone'])
SIG_DNS_REC_UPDATE = RobustSignal(providing_args=['zone', 'record'])

@receiver(post_save)
# pylint: disable=unused-argument
def dns_zone_update(sender, instance, created, **kwargs):
    """
    Trigger SIG_DNS_ZONE_UPDATE when new record is created or updated
    """
    from supervisr.dns.models import Zone
    if isinstance(instance, Zone):
        SIG_DNS_ZONE_UPDATE.send(sender, zone=instance)

@receiver(post_save)
# pylint: disable=unused-argument
def dns_rec_update(sender, instance, created, **kwargs):
    """
    Trigger SIG_DNS_REC_UPDATE when new record is created or updated
    """
    from supervisr.dns.models import Record
    if isinstance(instance, Record):
        SIG_DNS_REC_UPDATE.send(sender, record=instance, zone=instance.record_zone)

@receiver([SIG_DNS_REC_UPDATE, SIG_DNS_ZONE_UPDATE])
# pylint: disable=unused-argument
def dns_serial_update(sender, zone, **kwargs):
    """Update SOA Serial when zone is changed or record changed"""
    pass
    # soa = zone.soa
    # # Check if there is an updated record this is triggered by
    # # and if that record is SOA dont run again
    # if 'record' in kwargs:
    #     if kwargs['record'].type == 'SOA':
    #         LOGGER.debug("Not updating serial since SOA was updated")
    #         return
    # if soa:
    #     # SOA record exists, increase serial
    #     try:
    #         rdata = rec_to_rd(soa)
    #         now = datetime.now()
    #         serial_rev = int(str(rdata.serial)[-2:])
    #         serial_prefix = int(str(rdata.serial)[:-2])
    #         new_prefix = int("%04d%02d%02d" % (now.year, now.month, now.day))
    #         if serial_prefix == new_prefix:
    #             # If prefix is the same, we're on the same date. only increase rev
    #             serial_rev += 1
    #         else:
    #             # otherwise this is a different date. so start with a new revision
    #             serial_rev = 1
    #         # Build Serial after standard format, based on date and revision
    #         serial = int("%s%02d" % (new_prefix, serial_rev))
    #         LOGGER.debug("Updated SOA Serial from '%s' to '%s'", rdata.serial, serial)
    #         rdata.serial = serial
    #         soa.content = rdata.to_text()
    #         soa.save()
    #     except DNSSyntaxError:
    #         pass
