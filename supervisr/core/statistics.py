"""
Supervisr Core Statistics Wrapper
"""

from supervisr.core.signals import SIG_SET_STAT


def stat_set(key, value):
    """
    Wrapper to easily set a statistic
    """
    return SIG_SET_STAT.send(key=key, value=value, sender=stat_set)
