"""
Supervisr Core NavApps Templatetag
"""

import logging

from django import template
from django.apps import apps
from django.core.cache import cache
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

from supervisr.core.utils import get_apps

register = template.Library()

LOGGER = logging.getLogger(__name__)

@register.simple_tag(takes_context=True)
def supervisr_dyn_navapps(context):
    """
    Get a list of subapps for the navbar
    """
    # pylint: disable=global-statement
    key = 'supervisr_dyn_navapps'
    if not cache.get(key):
        app_list = []
        sub_apps = get_apps(mod_only=False)
        for mod in sub_apps:
            LOGGER.debug("Considering %s for Navbar", mod)
            config = None
            # Try new labels first
            try:
                mod_new = '/'.join(mod.split('.')[:-2])
                config = apps.get_app_config(mod_new)
                mod = mod_new
            except LookupError:
                mod = mod.split('.')[:-2][-1]
                config = apps.get_app_config(mod)
            title = config.title_moddifier(config.label, context.request)
            if config.navbar_enabled(context.request):
                mod = mod.replace('supervisr.', '')
                index = '%s:%s-index' % (mod, mod)
                try:
                    reverse(index)
                    LOGGER.debug("Mod %s made it with '%s'", mod, index)
                    app_list.append({
                        'short': mod,
                        'title': title,
                        'index': index
                        })
                except NoReverseMatch:
                    LOGGER.debug("View '%s' not reversable, ignoring %s", index, mod)
        cache.set(key, sorted(app_list, key=lambda x: x['short']), 1000)
    return cache.get(key)
