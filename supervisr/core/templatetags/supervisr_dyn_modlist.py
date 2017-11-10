"""
Supervisr Core ModList Templatetag
"""

from django import template
from django.apps import apps
from django.core.cache import cache

from supervisr.core.utils import get_apps

register = template.Library()

@register.simple_tag(takes_context=True)
def supervisr_dyn_modlist(context):
    """
    Get a list of all modules and their admin page
    """
    uniq = ''
    if 'request' in context:
        user = context.get('request').user
        if user.is_authenticated:
            uniq = context.get('request').user.email
        else:
            uniq = 'anon'
    key = 'supervisr_dyn_modlist_%s' % uniq
    if not cache.get(key):
        mod_list = get_apps(mod_only=True)
        view_list = []
        for mod in mod_list:
            config = None
            try:
                mod_new = '/'.join(mod.split('.')[:-2])
                config = apps.get_app_config(mod_new)
                mod = mod_new
            except LookupError:
                mod = mod.split('.')[:-2][-1]
                config = apps.get_app_config(mod)
            title = config.title_modifier(config.label, context.request)
            view_list.append({
                'url': apps.get_app_config(mod).admin_url_name,
                'name': title,
                })
        sorted_list = sorted(view_list, key=lambda x: x['name'])
        cache.set(key, sorted_list, 1000)
        return sorted_list
    return cache.get(key) # pragma: no cover
