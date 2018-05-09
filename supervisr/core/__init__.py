"""Supervisr Core Header"""
from __future__ import absolute_import, unicode_literals
from supervisr.core.celery import CELERY_APP as celery_app # noqa
__ui_name__ = 'Supervisr Core'
__author__ = 'Supervisr Team'
__email__ = 'supervisr@beryju.org'
__version__ = '0.1.2.2'

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.

__all__ = ('celery_app',)
