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
        try:
            # Old label style ('core', 'client', etc)
            app_title = context.request.resolver_match.namespace.split('/')[-1]
            dj_app = apps.get_app_config(app_title)
        except (LookupError, KeyError):
            # New label style ('supervisr/core', 'supervisr/mod/auth/oauth/client', etc)
            app_title = context.request.resolver_match.namespace
            dj_app = apps.get_app_config(app_title)
        title_moddifier = getattr(dj_app, 'title_moddifier', None)
        if title_moddifier:
            app_title = dj_app.title_moddifier(
                context.request.resolver_match.namespace, context.request)
            app = app_title + ' -'
    return _("%(title)s - %(app)s %(branding)s" % {
        'title': title,
        'branding': branding,
        'app': app,
        })
