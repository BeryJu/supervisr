"""
Supervisr Core NavApps Templatetag
"""

from django import template
from django.core.cache import cache
from supervisr.core.utils import get_apps

register = template.Library()


@register.simple_tag(takes_context=True)
def supervisr_dyn_user(context):
    """
    Get a list of modules that have custom user settings
    """
    uniq = ''
    if 'request' in context:
        user = context.get('request').user
        if user.is_authenticated:
            uniq = context.get('request').user.email
        else:
            uniq = 'anon'
    key = 'supervisr_dyn_user_%s' % uniq
    if not cache.get(key):
        app_list = []
        sub_apps = get_apps()
        for mod in sub_apps:
            if not mod.name.startswith('supervisr.mod'):
                continue
            view = mod.view_user_settings
            if view is not None:
                view = '%s:%s' % (mod.label, view)
                title = mod.title_modifier(context.request)
                app_list.append({
                    'title': title,
                    'view': view
                })
        sorted_list = sorted(app_list, key=lambda x: x['title'])
        cache.set(key, sorted_list, 1000)
        return sorted_list
    return cache.get(key)  # pragma: no cover
