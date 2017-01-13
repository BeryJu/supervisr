from django import template
from django.conf import settings

register = template.Library()

BLOCKED_SETTINGS = ['SECRET_KEY', 'LDAP', 'DATABASES']

@register.simple_tag
def setting(key, default=''):
    if key not in BLOCKED_SETTINGS:
        return getattr(settings, key, default)