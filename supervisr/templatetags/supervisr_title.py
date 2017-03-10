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
    branding = Setting.get('supervisr:branding')
    if title is None or title is '':
        return branding
    else:
        return _("%(title)s - %(branding)s" % {
            'title': title,
            'branding': branding
            })
