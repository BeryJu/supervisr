"""Supervisr Core Templatetags"""
import glob
import os
import socket
from urllib.parse import urljoin

from django import template
from django.apps import apps
from django.conf import settings
from django.db.models import Model
from django.template.loaders.app_directories import get_app_template_dirs
from django.urls import reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import Setting, UserAcquirable
from supervisr.core.utils import is_url_absolute, path_to_class

register = template.Library()


@register.simple_tag(takes_context=True)
def back(context):
    """Return a link back (either from GET paramter or referer."""

    request = context.get('request')
    url = ''
    if 'HTTP_REFERER' in request.META:
        url = request.META.get('HTTP_REFERER')
    if 'back' in request.GET:
        url = request.GET.get('back')

    if not is_url_absolute(url):
        return url
    return ''


@register.filter('fieldtype')
def fieldtype(field):
    """Return classname"""
    if isinstance(field.__class__, Model) or issubclass(field.__class__, Model):
        return field._meta.verbose_name
    return field.__class__.__name__


@register.simple_tag
def setting(key, default=''):
    """Returns a setting from the settings.py file. If Key is blocked, return default"""
    return getattr(settings, key, default)


@register.simple_tag
def hostname():
    """Return the current Host's short hostname"""
    return socket.gethostname()


@register.simple_tag
def fqdn():
    """Return the current Host's FQDN."""
    return socket.getfqdn()


@register.filter('pick')
def pick(cont, arg, fallback=''):
    """Iterate through arg and return first choice which is not None"""
    choices = arg.split(',')
    for choice in choices:
        if choice in cont and cont[choice] is not None:
            return cont[choice]
    return fallback


@register.simple_tag(takes_context=True)
def title(context, *title):
    """Return either just branding or title - branding"""
    branding = Setting.get('branding', default='supervisr')
    if not title:
        return branding
    # Include App Title in title
    app = ''
    if context.request.resolver_match and context.request.resolver_match.namespace != '':
        dj_app = None
        namespace = context.request.resolver_match.namespace.split(':')[0]
        # New label (App URL Namespace == App Label)
        dj_app = apps.get_app_config(namespace)
        title_modifier = getattr(dj_app, 'title_modifier', None)
        if title_modifier:
            app_title = dj_app.title_modifier(context.request)
            app = app_title + ' -'
    return _("%(title)s - %(app)s %(branding)s" % {
        'title': ' - '.join([str(x) for x in title]),
        'branding': branding,
        'app': app,
    })


@register.simple_tag
def supervisr_setting(key, namespace='supervisr.core', default=''):
    """Get a setting from the database. Returns default is setting doesn't exist."""
    return Setting.get(key=key, namespace=namespace, default=default)


@register.simple_tag()
def media(*args):
    """Iterate through arg and return full media URL"""
    urls = []
    for arg in args:
        urls.append(urljoin(settings.MEDIA_URL, str(arg)))
    if len(urls) == 1:
        return urls[0]
    return urls


@register.simple_tag
def url_unpack(view, kwargs):
    """Reverses a URL with kwargs which are stored in a dict"""
    return reverse(view, kwargs=kwargs)


@register.simple_tag
def template_wildcard(*args):
    """Return a list of all templates in dir"""
    templates = []
    for tmpl_dir in args:
        for app_templates in get_app_template_dirs('templates'):
            path = os.path.join(app_templates, tmpl_dir)
            if os.path.isdir(path):
                files = sorted(glob.glob(path + '*.html'))
                for file in files:
                    templates.append(os.path.relpath(file, start=app_templates))
    return templates


@register.simple_tag(takes_context=True)
def related_models(context, model_path):
    """Return list of models which have a Relationship to current user"""

    request = context.get('request', None)
    if not request:
        # No Request -> no user -> return empty
        return []
    user = request.user

    model = path_to_class(model_path)
    if not issubclass(model, UserAcquirable):
        # model_path is not actually a module
        # so we can't assume that it's usable
        return []

    return model.objects.filter(users__in=[user])


@register.filter('unslug')
def unslug(_input):
    """Convert slugs back into normal strings"""
    return _input.replace('-', ' ').replace('_', ' ')
