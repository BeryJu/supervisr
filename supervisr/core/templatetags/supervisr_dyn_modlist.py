"""
Supervisr Core ModList Templatetag
"""

from django import template
from django.core.cache import cache
from supervisr.core.apps import SupervisrAppConfig
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
            # This should never be reached as modlist requires admin rights
            uniq = 'anon'  # pragma: no cover
    key = 'supervisr_dyn_modlist_%s' % uniq
    if not cache.get(key):
        mod_list = get_apps()
        view_list = []
        for mod in mod_list:
            title = mod.title_modifier(context.request)
            url = mod.admin_url_name
            view_list.append({
                'url': url,
                'default': True if url == SupervisrAppConfig.admin_url_name else False,
                'name': title,
            })
        sorted_list = sorted(view_list, key=lambda x: x['name'])
        cache.set(key, sorted_list, 1000)
        return sorted_list
    return cache.get(key)  # pragma: no cover
