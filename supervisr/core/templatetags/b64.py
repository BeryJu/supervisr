"""
Supervisr Core Base64 filter
"""

import base64

from django import template
from django.core.files.base import File

from supervisr.core.utils import time

register = template.Library()

@register.filter('b64encode')
def b64encode(field):
    """
    Return encoded data
    """
    @time('b64encode_convert')
    def b64encode_inner(field):
        """
        Return encoded data
        """
        if isinstance(field, File):
            return base64.b64encode(field.read())
        return base64.b64encode(field)
    return b64encode_inner(field)
