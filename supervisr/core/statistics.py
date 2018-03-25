"""Supervisr Core Statistics Wrapper"""


def stat_set(key, value):
    """Wrapper to easily set a statistic"""
    from supervisr.core.tasks import stat_proxy
    return stat_proxy.delay(key, value)
