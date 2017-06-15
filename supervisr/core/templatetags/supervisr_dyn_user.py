"""
Supervisr Core NavApps Templatetag
"""

from django import template
from django.apps import apps

from ..utils import get_apps

register = template.Library()

APP_LIST = []

@register.simple_tag
def supervisr_dyn_user():
    """
    Get a list of modules that have custom user settings
    """
    # pylint: disable=global-statement
    global APP_LIST
    sub_apps = get_apps(mod_only=False)
    if APP_LIST == []:
        for mod in sub_apps:
            if 'mod' in mod:
                mod = mod.split('.')[:-2][-1]
            else:
                mod = mod.split('.')[1]
            view = apps.get_app_config(mod).view_user_settings
            if view is not None:
                view = '%s:%s' % (mod, view)
                mod = mod.replace('supervisr.', '').replace('mod.', '')
                APP_LIST.append({
                    'title': mod.title(),
                    'view': view
                    })
        APP_LIST = sorted(APP_LIST, key=lambda x: x['title'])
    return APP_LIST
