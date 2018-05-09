"""
Supervisr Core NavApps Templatetag
"""

import logging

from django import template
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
    uniq = ''
    if 'request' in context:
        user = context.get('request').user
        if user.is_authenticated:
            uniq = context.get('request').user.email
        else:
            uniq = 'anon'
    key = 'supervisr_dyn_navapps_%s' % uniq
    if not cache.get(key):
        app_list = []
        sub_apps = get_apps()
        for app in sub_apps:
            LOGGER.debug("Considering %s for Navbar", app.label)
            title = app.title_modifier(context.request)
            if app.navbar_enabled(context.request):
                index = getattr(app, 'index', None)
                if not index:
                    index = '%s:index' % app.label
                try:
                    reverse(index)
                    LOGGER.debug("Mod %s made it with '%s'", app.name, index)
                    app_list.append({
                        'label': app.label,
                        'title': title,
                        'index': index
                    })
                except NoReverseMatch:
                    LOGGER.debug("View '%s' not reversable, ignoring %s", index, app.name)
        sorted_list = sorted(app_list, key=lambda x: x.get('label'))
        cache.set(key, sorted_list, 1000)
        return sorted_list
    return cache.get(key)  # pragma: no cover
