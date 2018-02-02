"""
Supervisr Core navbar Templatetag
"""
import logging

from django import template

from supervisr.core.utils import get_app_labels

register = template.Library()

LOGGER = logging.getLogger(__name__)

@register.simple_tag()
def ifapp(*args):
    """
    Return whether a navbar link is active or not.
    """

    app_cache = get_app_labels()
    for app_label in args:
        if app_label in app_cache:
            return True
    return False
