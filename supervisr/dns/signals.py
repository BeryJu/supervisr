"""Supervisr DNS Signals"""
import logging
from datetime import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from supervisr.core.signals import RobustSignal
from supervisr.dns.models import Record, Zone

LOGGER = logging.getLogger(__name__)

SIG_DNS_ZONE_UPDATE = RobustSignal(providing_args=['zone'])
SIG_DNS_REC_UPDATE = RobustSignal(providing_args=['zone', 'record'])
SIG_DNS_RESOURCE_UPDATE = RobustSignal(providing_args=['resource_set'])


@receiver(post_save)
# pylint: disable=unused-argument
def dns_zone_update(sender, instance, created, **kwargs):
    """Trigger SIG_DNS_ZONE_UPDATE when new record is created or updated"""
    if isinstance(instance, Zone):
        SIG_DNS_ZONE_UPDATE.send(sender, zone=instance)


@receiver(post_save)
# pylint: disable=unused-argument
def dns_rec_update(sender, instance, created, **kwargs):
    """Trigger SIG_DNS_REC_UPDATE when new record is created or updated"""
    if isinstance(instance, Record):
        SIG_DNS_REC_UPDATE.send(sender, record=instance, zone=instance.record_zone)


@receiver(SIG_DNS_REC_UPDATE)
# pylint: disable=unused-argument
def dns_serial_update(sender, zone: Zone, **kwargs):
    """Update SOA Serial when zone is changed or record changed"""
    # SOA record exists, increase serial
    now = datetime.now()
    serial_rev = int(str(zone.soa_serial)[-2:])
    serial_prefix = int(str(zone.soa_serial)[:-2])
    new_prefix = int("%04d%02d%02d" % (now.year, now.month, now.day))
    if serial_prefix == new_prefix:
        # If prefix is the same, we're on the same date. only increase rev
        serial_rev += 1
    else:
        # otherwise this is a different date. so start with a new revision
        serial_rev = 1
    # Build Serial after standard format, based on date and revision
    serial = int("%s%02d" % (new_prefix, serial_rev))
    LOGGER.debug("Updated SOA Serial from '%s' to '%s'", zone.soa_serial, serial)
    zone.soa_serial = serial
    zone.save()
