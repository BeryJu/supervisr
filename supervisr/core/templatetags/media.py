"""
Supervisr Core Media Tag
"""

import urllib.parse


from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag()

def media(*args):
    """Iterate through arg and return full media URL"""
    urls = []
    for arg in args:
        urls.append(urllib.parse.urljoin(settings.MEDIA_URL, str(arg)))
    if len(urls) == 1:
        return urls[0]
    return urls
