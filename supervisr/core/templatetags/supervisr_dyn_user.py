"""
Supervisr Core NavApps Templatetag
"""

from django import template
from django.apps import apps

from ..utils import get_apps

register = template.Library()

APP_LIST = []

@register.simple_tag(takes_context=True)
def supervisr_dyn_user(context):
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
            config = apps.get_app_config(mod)
            view = config.view_user_settings
            if view is not None:
                view = '%s:%s' % (mod, view)
                mod = mod.replace('supervisr.', '').replace('mod.', '')
                title = config.title_moddifier(config.label, context.request)
                APP_LIST.append({
                    'title': title,
                    'view': view
                    })
        APP_LIST = sorted(APP_LIST, key=lambda x: x['title'])
    return APP_LIST
