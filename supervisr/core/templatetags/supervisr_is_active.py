"""Supervisr Core navbar Templatetag"""
import logging
import warnings

from django import template
from django.urls import reverse

register = template.Library()

LOGGER = logging.getLogger(__name__)


@register.simple_tag(takes_context=True)
def is_active(context, *urls, **kwargs):
    """Return whether a navbar link is active or not."""
    request = context.get('request')
    app_name = kwargs.get('app_name', None)
    active_class = kwargs.get('active_class', 'active')
    if not request.resolver_match:
        return ''
    # Monkeypatch app_name: urls from core have app_name == ''
    # since the root urlpatterns have no namespace
    if request.resolver_match.app_name == '':
        request.resolver_match.app_name = 'supervisr_core'
    for url in urls:
        short_url = url.split(':')[1] if ':' in url else url
        # Check if resolve_match matches
        if request.resolver_match.url_name.startswith(url) or \
                request.resolver_match.url_name.startswith(short_url):
            if app_name and request.resolver_match.app_name == app_name:
                return active_class
            elif app_name is None:
                return active_class
    # Return true if just app_name matches and no urls were given
    if not urls and app_name:
        if request.resolver_match.app_name == app_name:
            return active_class
    return ''


@register.simple_tag(takes_context=True)
def is_active_url(context, view, *args, **kwargs):
    """Return whether a navbar link is active or not."""

    matching_url = reverse(view, args=args, kwargs=kwargs)
    request = context.get('request')
    if not request.resolver_match:
        return ''
    if matching_url == request.path:
        return 'active'
    return ''


@register.simple_tag(takes_context=True)
def is_active_app(context, *args):
    """Return True if current link is from app"""
    warnings.warn('{% is_active_app %} is deprecated. Use {% is_active app_name= %} instead.')
    request = context.get('request')
    if not request.resolver_match:
        return ''
    for app_name in args:
        if request.resolver_match.app_name == app_name:
            return 'active'
    return ''
