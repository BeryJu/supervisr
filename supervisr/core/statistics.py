"""Supervisr Core Statistics Wrapper"""

from supervisr.core.tasks import stat_proxy


def stat_set(key, value):
    """Wrapper to easily set a statistic"""
    return stat_proxy.delay(key, value)
