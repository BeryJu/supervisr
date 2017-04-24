"""
Supervisr Core ModList Templatetag
"""

from django import template
from django.apps import apps

from ..utils import get_apps

register = template.Library()
VIEW_LIST = []

@register.simple_tag
def supervisr_dyn_modlist():
    """
    Get a list of all modules and their admin page
    """
    # pylint: disable=global-statement
    global VIEW_LIST
    mod_list = get_apps(mod_only=True)
    if VIEW_LIST == []:
        for mod in mod_list:
            if 'mod' in mod:
                mod = mod.split('.')[2]
            else:
                mod = mod.split('.')[1]
            name = mod.split('.')[-1]
            VIEW_LIST.append({
                'url': apps.get_app_config(mod).admin_url_name,
                'name': name,
                })
        VIEW_LIST = sorted(VIEW_LIST, key=lambda x: x['name'])
    return VIEW_LIST
