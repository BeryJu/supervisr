"""
Supervisr Core NavApps Templatetag
"""

from django import template
from django.apps import apps
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
        sub_apps = get_apps(mod_only=False)
        for mod in sub_apps:
            config = None
            try:
                mod_new = '/'.join(mod.split('.')[:-2])
                config = apps.get_app_config(mod_new)
                mod = mod_new
            except LookupError:
                if 'mod' in mod:
                    mod = mod.split('.')[:-2][-1]
                else:
                    mod = mod.split('.')[1]
                config = apps.get_app_config(mod)
            view = config.view_user_settings
            if view is not None:
                view = '%s:%s' % (mod, view)
                mod = mod.replace('supervisr.', '').replace('mod.', '')
                title = config.title_modifier(config.label, context.request)
                app_list.append({
                    'title': title,
                    'view': view
                    })
        sorted_list = sorted(app_list, key=lambda x: x['title'])
        cache.set(key, sorted_list, 1000)
        return sorted_list
    return cache.get(key) # pragma: no cover
