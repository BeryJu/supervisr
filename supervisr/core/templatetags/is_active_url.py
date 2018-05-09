"""
Supervisr Core navbar Templatetag
"""

from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def is_active_url(context, view, *args, **kwargs):
    """
    Return whether a navbar link is active or not.
    """
    matching_url = reverse(view, args=args, kwargs=kwargs)
    req = context['request']
    if not req.resolver_match:
        return ''
    if matching_url == req.path:
        return 'active'
    return ''
