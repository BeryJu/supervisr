"""Supervisr Core navbar Templatetag"""
from logging import getLogger

from django import template

from supervisr.core.utils import get_apps

register = template.Library()

LOGGER = getLogger(__name__)


@register.simple_tag()
def ifapp(*args):
    """Return whether a navbar link is active or not."""

    app_cache = [app.label for app in get_apps(exclude=[])]
    for app_label in args:
        if app_label in app_cache:
            return True
    return False
