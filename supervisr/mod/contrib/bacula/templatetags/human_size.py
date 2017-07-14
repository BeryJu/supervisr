"""
Supervisr Bacula Human Size
"""

from django import template

from supervisr.mod.contrib.bacula.utils import size_human

register = template.Library()
@register.simple_tag
def human_size(size):
    """
    Simple tag to huamnify size to other unites
    """
    return size_human(size)
