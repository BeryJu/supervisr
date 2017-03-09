"""
Supervisr Core ModList Templatetag
"""

from django import template
from django.apps import apps

from ..utils import get_apps

register = template.Library()

@register.simple_tag
def supervisr_modlist():
    """

    Get a setting from the database. Returns default is setting doesn't exist.
    """
    mod_list = get_apps(mod_only=True)
    view_list = []
    for mod in mod_list:
        if '.' in mod:
            name = mod.split('.')[-1]
            mod = mod.split('.')[0]
        else:
            name = mod
        view_list.append({
            'url': apps.get_app_config(mod).admin_url_name,
            'name': name,
            })

    return sorted(view_list, key=lambda x: x['name'])
