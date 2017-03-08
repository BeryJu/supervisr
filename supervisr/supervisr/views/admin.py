"""
Supervisr Core Admin Views
"""


import platform
import sys

from django import get_version as django_version
from django.conf import settings as django_settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render

from ..signals import SIG_GET_MOD_INFO
from ..utils import get_reverse_dns


@login_required
@user_passes_test(lambda u: u.is_superuser)
def index(req):
    """
    Admin index
    """
    # Subtract the system user
    user_count = User.objects.all().count() -1
    return render(req, '_admin/index.html', {
        'user_count': user_count,
        })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def settings(req):
    """
    Admin settings
    """
    return render(req, '_admin/index.html')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def mod_default(req, mod):
    """
    Default view for modules without admin view
    """
    return render(req, '_admin/mod_default.html', {
        'mod': mod
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
            'Supervisr Commit': django_settings.VERSION_HASH,
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
            'Debug Enabled': django_settings.DEBUG,
        }
    }
    results = SIG_GET_MOD_INFO.send(sender=None)
    for handler, mod_info in results:
        # Get the handler's root module
        info[handler.__module__.split('.')[0]] = mod_info
    return render(req, '_admin/info.html', {'info': info})
