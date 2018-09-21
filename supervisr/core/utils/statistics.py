"""Supervisr Core Statistics Wrapper"""


def set_statistic(key, value, **hints):
    """Wrapper to easily set a statistic"""
    from supervisr.core.tasks import statistic_task
    return statistic_task.apply_async(args=[key, value, hints], queue='supervisr_statistics')
