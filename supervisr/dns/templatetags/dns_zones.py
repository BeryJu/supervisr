"""
Supervisr DNS Zone Templatetag
"""
from django import template

from supervisr.dns.models import Zone

register = template.Library()

@register.simple_tag(takes_context=True)
def dns_zones(context):
    """
    Return list of zones for current user
    """
    if 'request' in context:
        return Zone.objects \
            .filter(users__in=[context['request'].user]) \
            .order_by('domain__domain')
    return []
