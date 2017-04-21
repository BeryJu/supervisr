"""
Supervisr Core Setting Templatetag
"""

from django import template

from ..models import Setting

register = template.Library()

@register.simple_tag
def supervisr_setting(key, default=''):
    """
    Get a setting from the database. Returns default is setting doesn't exist.
    """
    return Setting.get(
        "core:%s" % key, default)
