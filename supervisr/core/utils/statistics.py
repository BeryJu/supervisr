"""Supervisr Core Statistics Wrapper"""


def set_statistic(key, value, **hints):
    """Wrapper to easily set a statistic"""
    from supervisr.core.tasks import stat_proxy
    return stat_proxy.delay(key, value, hints)
