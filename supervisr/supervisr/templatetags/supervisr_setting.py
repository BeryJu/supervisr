from django import template
from ..models import *
register = template.Library()

@register.simple_tag
def supervisr_setting(key, default=''):
    return Setting.get(
        "supervisr:%s" % key, default).value