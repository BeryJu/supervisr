"""
Supervisr Core About Views
"""

import platform
import socket
import sys

from django import get_version
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from ..ldap_connector import LDAPConnector


def changelog(req):
    """
    Show Changelog, which is read from ../../CHANGELOG.md
    """
    return render(req, 'about/changelog.html', {
        'changelog': settings.CHANGELOG
        })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def info(req):
    """
    Show system information
    """
    data = {
        'Python Version': sys.version_info.__repr__(),
        'uname': platform.uname().__repr__(),
        'FQDN': socket.getfqdn(),
        'url_name': req.resolver_match.url_name,
        'commit': settings.VERSION_HASH,
        'django': get_version(),
        'LDAPConnector': LDAPConnector.enabled,
    }
    return render(req, 'about/info.html', {'data': data})
