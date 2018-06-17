"""
Supervisr Core Title Templatetag
"""

from django import template
from django.apps import apps
from django.utils.translation import ugettext as _
from supervisr.core.models import Setting

register = template.Library()


@register.simple_tag(takes_context=True)
def supervisr_title(context, title=None):
    """
    Return either just branding or title - branding
    """
    branding = Setting.get('branding')
    if title is None or title == '':
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
        'title': title,
        'branding': branding,
        'app': app,
    })
