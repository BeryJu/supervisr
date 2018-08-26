"""Supervisr Core Task APIv1"""

from django.http import HttpRequest

from supervisr.core.api.base import API
from supervisr.core.tasks import Progress


class TaskAPI(API):
    """Task API"""

    ALLOWED_VERBS = {
        'GET': ['progress']
    }

    @staticmethod
    def init_user_filter(user):
        """This method is used to check if the user has access"""
        return True

    # pylint: disable=unused-argument
    def progress(self, request: HttpRequest, data: dict) -> dict:
        """Get Progress info for task_id"""
        progress = Progress(data.get('id'))
        return progress.get_info()
