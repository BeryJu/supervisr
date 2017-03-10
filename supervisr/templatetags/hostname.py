"""
Supervisr Core Hostname Templatetag
"""
import socket

from django import template

register = template.Library()

@register.simple_tag
def hostname():
    """
    Return the current Host's short hostname
    """
    return socket.gethostname()

@register.simple_tag
def fqdn():
    """
    Return the current Host's FQDN.
    """
    return socket.getfqdn()
