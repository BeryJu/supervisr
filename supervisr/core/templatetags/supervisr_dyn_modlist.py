"""
Supervisr Core ModList Templatetag
"""

from django import template
from django.apps import apps

from ..utils import get_apps

register = template.Library()

@register.simple_tag(takes_context=True)
def supervisr_dyn_modlist(context):
    """
    Get a list of all modules and their admin page
    """
    mod_list = get_apps(mod_only=True)
    view_list = []
    for mod in mod_list:
        mod = mod.split('.')[:-2][-1]
        config = apps.get_app_config(mod)
        title = config.title_moddifier(config.label, context.request)
        view_list.append({
            'url': apps.get_app_config(mod).admin_url_name,
            'name': title,
            })
    return sorted(view_list, key=lambda x: x['name'])
