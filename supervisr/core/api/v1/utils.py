"""Supervisr Core Utils APIv1"""

from django.http import HttpRequest
from django.shortcuts import reverse
from django.utils.translation import gettext

from supervisr.core.api.base import API


class UtilAPI(API):
    """Utils API"""

    ALLOWED_VERBS = {
        'GET': ['reverse', 'gettext']
    }

    def reverse(self, request: HttpRequest, data: dict) -> dict:
        """Get reversed URL"""
        view_name = data.pop('__view_name')
        return reverse(view_name, kwargs=data)

    def gettext(self, request: HttpRequest, data: dict) -> dict:
        """Translate string from request, applying formatting options from request"""
        message = data.pop("__message")
        return gettext(message % data)
