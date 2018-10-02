"""Supervisr Core Statistics Wrapper"""
from aenum import IntEnum
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from supervisr.core.celery import CELERY_APP


class StatisticType(IntEnum):
    """Statistic Type, change how value is saved"""

    Counter = 1
    Timing = 2
    AsIs = 1024

def set_statistic(key, hints=None, **values):
    """Wrapper to easily set a statistic"""
    task = CELERY_APP.tasks['supervisr.core.tasks.StatisticTask']
    CELERY_APP.control.add_consumer('supervisr:statistics')
    return task.apply_async(args=[key, values, hints], queue='supervisr:statistics')


@receiver(user_logged_in)
# pylint: disable=unused-argument
def statistic_user_logged_in(sender, user, **kwargs):
    """Handle stats for user_logged_in"""
    set_statistic('user.login', count={
        'value': 1,
        'type': StatisticType.Counter
    })


@receiver(user_logged_out)
# pylint: disable=unused-argument
def statistic_user_logged_out(sender, user, **kwargs):
    """Handle stats for user_logged_out"""
    set_statistic('user.logout', count={
        'value': 1,
        'type': StatisticType.Counter
    })
