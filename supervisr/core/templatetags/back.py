"""
Supervisr Core back Templatetag
"""

from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def back(context):
    """
    Return whether a back link is active or not.
    """
    req = context['request']
    if 'HTTP_REFERER' in req.META:
        return req.META.get('HTTP_REFERER')
    return ''
