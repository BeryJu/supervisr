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
    uniq = ''
    if 'request' in context:
        uniq = context['request'].user.email
    key = 'supervisr_dyn_navapps_%s' % uniq
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
            view_prefix = mod.split('/')[-1]
            title = config.title_moddifier(config.label, context.request)
            if config.navbar_enabled(context.request):
                mod = mod.replace('supervisr.', '')
                index = '%s:%s-index' % (mod, view_prefix)
                try:
                    reverse(index)
                    LOGGER.debug("Mod %s made it with '%s'", mod, index)
                    app_list.append({
                        'short': view_prefix,
                        'title': title,
                        'index': index
                        })
                except NoReverseMatch:
                    LOGGER.debug("View '%s' not reversable, ignoring %s", index, mod)
        sorted_list = sorted(app_list, key=lambda x: x['short'])
        cache.set(key, sorted_list, 1000)
        return sorted_list
    return cache.get(key) # pragma: no cover
