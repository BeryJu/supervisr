"""Supervisr Core Admin Views"""

import platform
import sys

import celery
from django import get_version as django_version
from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.cache import cache
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from revproxy.views import ProxyView
from supervisr.core.models import Event, Setting, User, get_system_user
from supervisr.core.signals import SIG_GET_MOD_INFO, SIG_SETTING_UPDATE
from supervisr.core.tasks import debug_progress_task
from supervisr.core.utils import get_reverse_dns
from supervisr.core.views.generic import AdminRequiredView


@login_required
@user_passes_test(lambda u: u.is_superuser)
def index(request: HttpRequest) -> HttpResponse:
    """Admin index"""
    # Subtract the system user
    user_count = User.objects.all().count() - 1
    celery_ping = celery.current_app.control.inspect().ping()
    return render(request, '_admin/index.html', {
        'user_count': user_count,
        'celery_workers': celery_ping
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def users(request: HttpRequest) -> HttpResponse:
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
def info(request: HttpRequest) -> HttpResponse:
    """Show system information"""
    info_data = {
        _('Version'): {
            _('Python Version'): sys.version_info.__repr__(),
            _('Django Version'): django_version(),
            _('Supervisr Commit'): django_settings.VERSION,
        },
        _('System'): {
            _('uname'): platform.uname().__repr__(),
        },
        _('Request'): {
            _('url_name'): (
                request.resolver_match.url_name if request.resolver_match is not None
                else ''),
            _('REMOTE_ADDR'): request.META.get('REMOTE_ADDR'),
            _('REMOTE_ADDR PTR'): get_reverse_dns(request.META.get('REMOTE_ADDR')),
            _('X-Forwarded-for'): request.META.get('HTTP_X_FORWARDED_FOR'),
            _('X-Forwarded-for PTR'): get_reverse_dns(request.META.get('HTTP_X_FORWARDED_FOR')),
        },
        _('Settings'): {
            _('Debug Enabled'): django_settings.DEBUG,
            _('Authentication Backends'): django_settings.AUTHENTICATION_BACKENDS,
        }
    }
    results = SIG_GET_MOD_INFO.send(sender=None)
    for handler, mod_info in results:
        # Get the handler's root module
        info_data[handler.__module__.split('.')[0]] = mod_info
    return render(request, '_admin/info.html', {'info': info_data})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def events(request: HttpRequest) -> HttpResponse:
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
def debug(request: HttpRequest) -> HttpResponse:
    """Show some misc debug buttons"""
    if request.method == 'POST':
        if 'raise_error' in request.POST:
            raise RuntimeError('test error')
        elif 'clear_cache' in request.POST:
            cache.clear()
            messages.success(request, _('Successfully cleared Cache'))
        elif 'update_settings' in request.POST:
            setting = Setting.get('domain')
            SIG_SETTING_UPDATE.send(sender=setting)
            messages.success(request, _('Successfully updated settings.'))
        elif 'start_task' in request.POST:
            seconds = int(request.POST.get('start_task_sec'))
            result = request.user.task_apply_async(debug_progress_task, seconds)
            messages.success(request, _('Started Task, ID: %(id)s' % {'id': result.id}))
    return render(request, '_admin/debug.html')


class FlowerView(AdminRequiredView):
    """View to show iframe with flower"""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Show template with iframe for flower"""
        return render(request, '_admin/flower.html')


class FlowerProxy(ProxyView, AdminRequiredView):
    """Flower Proxy"""
    upstream = 'http://localhost:5555'
