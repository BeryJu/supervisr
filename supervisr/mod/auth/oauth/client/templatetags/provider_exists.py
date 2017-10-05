"""
Supervisr Oauth Provider Exists Templatetag
"""

from django import template
from django.db.models import Q

from supervisr.mod.auth.oauth.client.models import Provider

register = template.Library()

@register.simple_tag
def provider_exists(name):
    """
    Return True if Provider exists
    """
    return True
    return Provider.objects.filter(Q(name=name) | Q(ui_name=name)).exists()

@register.simple_tag
def any_provider():
    """
    Return true if any provider exists
    """
    return True
    return Provider.objects.all().count() > 0
