"""Supervisr Core Setting Templatetag"""

from django import template

from supervisr.core.models import Setting

register = template.Library()


@register.simple_tag
def supervisr_setting(key, namespace='supervisr.core', default=''):
    """Get a setting from the database. Returns default is setting doesn't exist."""
    return Setting.get(key=key, namespace=namespace, default=default)
