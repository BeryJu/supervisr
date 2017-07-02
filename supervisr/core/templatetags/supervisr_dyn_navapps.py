"""
Supervisr Core NavApps Templatetag
"""

import logging

from django import template
from django.apps import apps
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

from ..utils import get_apps

register = template.Library()

LOGGER = logging.getLogger(__name__)

@register.simple_tag(takes_context=True)
def supervisr_dyn_navapps(context):
    """
    Get a list of subapps for the navbar
    """
    # pylint: disable=global-statement
    app_list = []
    sub_apps = get_apps(mod_only=False)
    for mod in sub_apps:
        LOGGER.debug("Considering %s for Navbar", mod)
        short_mod = mod.split('.')[:-2][-1]
        mod = '/'.join(mod.split('.')[:-2])
        config = apps.get_app_config(mod)
        title = config.title_moddifier(short_mod, context.request)
        if config.navbar_enabled(context.request):
            mod = mod.replace('.', '/')
            index = '%s:%s-index' % (mod, short_mod)
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
    return sorted(app_list, key=lambda x: x['short'])
