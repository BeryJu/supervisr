"""Supervisr Core Statistics Wrapper"""

from supervisr.core.celery import CELERY_APP


def set_statistic(key, value, **hints):
    """Wrapper to easily set a statistic"""
    from supervisr.core.tasks import statistic_task
    CELERY_APP.control.add_consumer('supervisr_statistics')
    return statistic_task.apply_async(args=[key, value, hints], queue='supervisr_statistics')
