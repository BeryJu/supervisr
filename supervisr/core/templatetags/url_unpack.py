"""Supervisr Core url_unpack templatetag"""

from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def url_unpack(view, kwargs):
    """Reverses a URL with kwargs which are stored in a dict"""
    return reverse(view, kwargs=kwargs)
