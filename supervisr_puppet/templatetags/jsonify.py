"""
Supervisr Puppet Templatetags
"""

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def jsonify(value):
    """
    Escape newlines to \n and "'s to \"
    """
    return "\\n".join(value.split('\n')).replace('"', '\\"')
