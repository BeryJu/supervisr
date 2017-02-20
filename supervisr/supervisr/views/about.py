"""
Supervisr Core About Views
"""

import platform
import sys

from django import get_version as django_version
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from ..signals import SIG_GET_MOD_INFO
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
            'Supervisr Commit': settings.VERSION_HASH,
        },
        'System': {
            'uname': platform.uname().__repr__(),
        },
        'Request': {
            'url_name': req.resolver_match.url_name if req.resolver_match is not None else '',
            'REMOTE_ADDR': req.META.get('REMOTE_ADDR'),
            'REMOTE_ADDR PTR': get_reverse_dns(req.META.get('REMOTE_ADDR')),
            'X-Forwarded-for': req.META.get('HTTP_X_FORWARDED_FOR'),
            'X-Forwarded-for PTR': get_reverse_dns(req.META.get('HTTP_X_FORWARDED_FOR')),
        },
        'Settings': {
            'Debug Enabled': settings.DEBUG,
        }
    }
    results = SIG_GET_MOD_INFO.send(sender=None)
    for handler, mod_info in results:
        info[handler.__module__.split('.')[0]] = mod_info
    return render(req, 'about/info.html', {'info': info})
