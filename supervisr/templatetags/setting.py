"""
Supervisr Core Setting Templatetag
"""

from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def setting(key, default=''):
    """
    Returns a setting from the settings.py file. If Key is blocked, return default
    """
    return getattr(settings, key, default)
