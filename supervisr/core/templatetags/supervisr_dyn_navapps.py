"""
Supervisr Core NavApps Templatetag
"""

from django import template
from django.apps import apps
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

from ..utils import get_apps

register = template.Library()

APP_LIST = []

@register.simple_tag(takes_context=True)
def supervisr_dyn_navapps(context):
    """
    Get a list of subapps for the navbar
    """
    # pylint: disable=global-statement
    global APP_LIST
    sub_apps = get_apps(mod_only=False)
    if APP_LIST == []:
        for mod in sub_apps:
            mod = mod.split('.')[:-2][-1]
            config = apps.get_app_config(mod)
            title = config.title_moddifier(config.label, context.request)
            if config.navbar_enabled(context.request):
                mod = mod.replace('supervisr.', '')
                index = '%s:%s-index' % (mod, mod)
                try:
                    reverse(index)
                    APP_LIST.append({
                        'short': mod,
                        'title': title,
                        'index': index
                        })
                except NoReverseMatch:
                    pass
        APP_LIST = sorted(APP_LIST, key=lambda x: x['short'])
    return APP_LIST
