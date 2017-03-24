"""
Supervisr Core NavApps Templatetag
"""

from django import template
from django.apps import apps

from ..utils import get_apps

register = template.Library()

APP_LIST = []

@register.simple_tag
def supervisr_navapps():
    """
    Get a list of subapps for the navbar
    """
    # pylint: disable=global-statement
    global APP_LIST
    sub_apps = get_apps(mod_only=False)
    if APP_LIST == []:
        for mod in sub_apps:
            if 'mod' not in mod:
                if '.' in mod:
                    mod = mod.split('.')[0]
                title = apps.get_app_config(mod).navbar_title
                mod = mod.replace('supervisr_', '')
                if title is None:
                    title = mod.title()
                APP_LIST.append({
                    'short': mod,
                    'title': title,
                    'index': 'supervisr_%s:%s-index' % (mod, mod)
                    })
        APP_LIST = sorted(APP_LIST, key=lambda x: x['short'])
    return APP_LIST
