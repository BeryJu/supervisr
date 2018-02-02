"""
Supervisr Core Pick filter
"""

from django import template

register = template.Library()

@register.filter('pick')
def pick(cont, arg, fallback=''):
    """
    Iterate through arg and return first choice which is not None
    """
    choices = arg.split(',')
    for choice in choices:
        if choice in cont and cont[choice] is not None:
            return cont[choice]
    return fallback
