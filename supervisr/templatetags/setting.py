"""
Supervisr Core Setting Templatetag
"""

from django import template
from django.conf import settings

register = template.Library()

BLOCKED_SETTINGS = ['SECRET_KEY', 'DATABASES']

@register.simple_tag
def setting(key, default=''):
    """
    Returns a setting from the settings.py file. If Key is blocked, return default
    """
    if key not in BLOCKED_SETTINGS:
        return getattr(settings, key, default)
    return default
