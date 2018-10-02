"""Supervisr Stats influx Signals"""

from django.dispatch import receiver

from supervisr.core.models import Setting
from supervisr.core.signals import get_module_health, on_set_statistic
from supervisr.mod.stats.influx.influx_client import InfluxClient


@receiver(get_module_health)
# pylint: disable=unused-argument
def stats_influx_handle_health(sender, **kwargs):
    """Create initial settings needed"""
    if Setting.get_bool('enabled'):
        with InfluxClient():
            return True
    else:
        return True


@receiver(on_set_statistic)
# pylint: disable=unused-argument
def stats_influx_handle_set_stat(sender, name, values, hints, **kwargs):
    """Handle stats for SET_STAT"""
    if Setting.get_bool('enabled'):
        with InfluxClient() as client:
            client.write(name, hints, **values)
