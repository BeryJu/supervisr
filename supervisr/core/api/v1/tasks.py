"""Supervisr Core Task APIv1"""

from django.http import HttpRequest

from supervisr.core.api.base import API
from supervisr.core.tasks import Progress


class TaskAPI(API):
    """Task API"""

    ALLOWED_VERBS = {
        'GET': ['progress']
    }

    def progress(self, request: HttpRequest, data: dict) -> dict:
        """Get Progress info for task_id"""
        progress = Progress(data.get('id'))
        return progress.get_info()
