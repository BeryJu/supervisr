"""
Supervisr Core Admin Views
"""


import platform
import sys

from django import get_version as django_version
from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import redirect, render
from django.urls import reverse

from ..models import Event
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
def info(req):
    """
    Show system information
    """
    info_data = {
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
        info_data[handler.__module__.split('.')[0]] = mod_info
    return render(req, '_admin/info.html', {'info': info_data})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def events(req):
    """
    Show paginated list of all events
    """
    event_list = Event.objects.all().order_by('-create_date')
    paginator = Paginator(event_list, 25)

    page = req.GET.get('page')
    try:
        event_page = paginator.page(page)
    except PageNotAnInteger:
        event_page = paginator.page(1)
    except EmptyPage:
        event_page = paginator.page(paginator.num_pages)

    return render(req, '_admin/events.html', {'events': event_page})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def debug(req):
    """
    Show some misc debug buttons
    """
    return render(req, '_admin/debug.html')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def debug_puppet_build(req):
    """
    Run Puppet Build
    """
    from supervisr.puppet.builder import ReleaseBuilder
    from supervisr.puppet.models import PuppetModule
    module = PuppetModule.objects.filter(name='supervisr_mail').first()
    rel_builder = ReleaseBuilder(module)
    rel_builder.build()
    messages.success(req, 'Successfully built')
    return redirect(reverse('admin-debug'))
