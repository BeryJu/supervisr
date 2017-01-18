"""
Supervisr Core navbar Templatetag
"""

from django import template

from ..models import Setting

register = template.Library()

@register.simple_tag(takes_context=True)
def is_active(context, *args):
    """
    Return whether a navbar link is active or not.
    """
    req = context['request']
    for url in args:
        if req.resolver_match.url_name.startswith(url):
            return 'active'
    return ''
