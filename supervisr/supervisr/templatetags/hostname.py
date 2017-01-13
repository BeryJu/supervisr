import socket

from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def hostname():
    return socket.gethostname()

@register.simple_tag
def fqdn():
    return socket.getfqdn()
