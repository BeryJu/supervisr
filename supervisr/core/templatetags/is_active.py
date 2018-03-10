"""Supervisr Core navbar Templatetag"""
import logging

from django import template

register = template.Library()

LOGGER = logging.getLogger(__name__)


@register.simple_tag(takes_context=True)
def is_active(context, *args, **kwargs):
    """Return whether a navbar link is active or not."""
    request = context.get('request')
    app_name = kwargs.get('app_name', None)
    if not request.resolver_match:
        return ''
    for url in args:
        short_url = url.split(':')[1] if ':' in url else url
        # Check if resolve_match matches
        if request.resolver_match.url_name.startswith(url) or \
                request.resolver_match.url_name.startswith(short_url):
            # Monkeypatch app_name: urls from core have app_name == ''
            # since the root urlpatterns have no namespace
            if request.resolver_match.app_name == '':
                request.resolver_match.app_name = 'supervisr_core'
            if app_name and request.resolver_match.app_name == app_name:
                return 'active'
            elif app_name is None:
                return 'active'
    return ''
