"""Supervisr DNS Signals"""
import logging
from datetime import datetime
from typing import List

from django.db.models.signals import post_save
from django.dispatch import receiver

from supervisr.core.signals import RobustSignal
from supervisr.dns.models import BaseRecord, Zone

LOGGER = logging.getLogger(__name__)

on_dns_zone_update = RobustSignal(
    stat_name="on_dns_zone_update", providing_args=['zone'])
on_dns_record_update = RobustSignal(
    stat_name="on_dns_record_update", providing_args=['record', 'zones'])

@receiver(post_save)
# pylint: disable=unused-argument
def dns_zone_update(sender, instance, created, **kwargs):
    """Trigger on_dns_zone_update when new record is created or updated"""
    if isinstance(instance, Zone):
        on_dns_zone_update.send(sender, zone=instance)


@receiver(post_save)
# pylint: disable=unused-argument
def dns_record_update(sender, instance, created, **kwargs):
    """Trigger on_dns_record_update when new record is created or updated"""
    if isinstance(instance, BaseRecord):
        on_dns_record_update.send(sender, record=instance.cast(), zones=instance.zone_set.all())


@receiver(on_dns_record_update)
# pylint: disable=unused-argument
def dns_serial_update(sender, zones: List[Zone], **kwargs):
    """Update SOA Serial when zone is changed or record changed"""
    for zone in zones:
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
