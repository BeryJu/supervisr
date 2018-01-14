"""
Supervisr Core Admin Views
"""


import platform
import sys

from django import get_version as django_version
from django.conf import settings as django_settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render

from supervisr.core.models import Event, User, get_system_user
from supervisr.core.signals import SIG_GET_MOD_INFO
from supervisr.core.utils import get_reverse_dns


@login_required
@user_passes_test(lambda u: u.is_superuser)
def index(request):
    """Admin index"""
    # Subtract the system user
    user_count = User.objects.all().count() -1
    return render(request, '_admin/index.html', {
        'user_count': user_count,
        })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def users(request):
    """Show a list of all users"""
    users = User.objects.all().order_by('date_joined').exclude(pk=get_system_user())
    paginator = Paginator(users, request.user.rows_per_page)

    page = request.GET.get('page')
    try:
        accounts = paginator.page(page)
    except PageNotAnInteger:
        accounts = paginator.page(1)
    except EmptyPage:
        accounts = paginator.page(paginator.num_pages)
    return render(request, '_admin/users.html', {
        'users': accounts,
        })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def info(request):
    """Show system information"""
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
            'url_name': (
                request.resolver_match.url_name if request.resolver_match is not None
                else ''),
            'REMOTE_ADDR': request.META.get('REMOTE_ADDR'),
            'REMOTE_ADDR PTR': get_reverse_dns(request.META.get('REMOTE_ADDR')),
            'X-Forwarded-for': request.META.get('HTTP_X_FORWARDED_FOR'),
            'X-Forwarded-for PTR': get_reverse_dns(request.META.get('HTTP_X_FORWARDED_FOR')),
        },
        'Settings': {
            'Debug Enabled': django_settings.DEBUG,
            'Authentication Backends': django_settings.AUTHENTICATION_BACKENDS,
        }
    }
    results = SIG_GET_MOD_INFO.send(sender=None)
    for handler, mod_info in results:
        # Get the handler's root module
        info_data[handler.__module__.split('.')[0]] = mod_info
    return render(request, '_admin/info.html', {'info': info_data})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def events(request):
    """Show paginated list of all events"""
    event_list = Event.objects.all().order_by('-create_date')
    paginator = Paginator(event_list, request.user.rows_per_page)

    page = request.GET.get('page')
    try:
        event_page = paginator.page(page)
    except PageNotAnInteger:
        event_page = paginator.page(1)
    except EmptyPage:
        event_page = paginator.page(paginator.num_pages)

    return render(request, '_admin/events.html', {'events': event_page})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def debug(request):
    """Show some misc debug buttons"""
    if request.method == 'POST':
        if 'raise_error' in request.POST:
            raise RuntimeError('test error')
    return render(request, '_admin/debug.html')
