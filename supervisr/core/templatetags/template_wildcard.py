"""
Supervisr Core templte_wildcard Templatetag
"""

import glob
import os

from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def template_wildcard(tmpl_dir):
    """
    Return a list of all templates in dir
    """
    for app in settings.INSTALLED_APPS:
        if app.startswith('supervisr'):
            app_dir = '/'.join(app.split('.')[1:-2])
            prefix = os.path.abspath(os.path.join(settings.BASE_DIR, app_dir, 'templates/'))
            path = os.path.join(prefix, tmpl_dir)
            if os.path.isdir(path):
                files = glob.glob(path+'**')
                templates = []
                for file in files:
                    templates.append(os.path.relpath(file, start=prefix))
                    return templates
    return []
