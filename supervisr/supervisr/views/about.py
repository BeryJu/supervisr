"""
Supervisr Core About Views
"""

import platform
import socket
import sys

from django import get_version as django_version
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from ldap3 import version as ldap3_version

from ..ldap_connector import LDAPConnector
from ..utils import get_reverse_dns


def changelog(req):
    """
    Show Changelog, which is read from ../../CHANGELOG.md
    """
    return render(req, 'about/changelog.html', {
        'changelog': settings.CHANGELOG
        })

@login_required
@user_passes_test(lambda u: u.is_superuser)
# pylint:disable=redefined-outer-name
def info(req):
    """
    Show system information
    """
    info = {
        'Version': {
            'Python Version': sys.version_info.__repr__(),
            'Django Version': django_version(),
            'LDAP3 Version': ldap3_version.__version__,
            'Supervisr Commit': settings.VERSION_HASH,
        },
        'System': {
            'uname': platform.uname().__repr__(),
            'FQDN': socket.getfqdn(),
        },
        'Request': {
            'url_name': req.resolver_match.url_name,
            'REMOTE_ADDR': req.META.get('REMOTE_ADDR'),
            'REMOTE_ADDR PTR': get_reverse_dns(req.META.get('REMOTE_ADDR')),
            'X-Forwarded-for': req.META.get('HTTP_X_FORWARDED_FOR'),
            'X-Forwarded-for PTR': get_reverse_dns(req.META.get('HTTP_X_FORWARDED_FOR')),
        },
        'Settings': {
            'LDAP Enabled': LDAPConnector.enabled,
            'Debug Enabled': settings.DEBUG,
        }
    }
    return render(req, 'about/info.html', {'info': info})
