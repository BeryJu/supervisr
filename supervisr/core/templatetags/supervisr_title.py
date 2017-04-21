"""
Supervisr Core Title Templatetag
"""

from django import template
from django.utils.translation import ugettext as _

from ..models import Setting

register = template.Library()

@register.simple_tag
def supervisr_title(title=None):
    """
    Return either just branding or title - branding
    """
    branding = Setting.get('core:branding')
    if title is None or title == '':
        return branding
    return _("%(title)s - %(branding)s" % {
        'title': title,
        'branding': branding
        })
