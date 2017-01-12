from django import template
from ..models import *
register = template.Library()

@register.simple_tag
def supervisr_setting(key, default=''):
    setting, created = Setting.objects.get_or_create(
        key="supervisr:%s" % key,
        defaults={'value': default})
    return setting.value