"""Supervisr Core Admin Views"""

import platform
import sys

import celery
from django import get_version as django_version
from django.conf import settings as django_settings
from django.contrib import messages
from django.core.cache import cache
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateView

from supervisr.core.mailer import send_message
from supervisr.core.models import Event, Setting, Task, User, get_system_user
from supervisr.core.signals import get_module_info, on_setting_update
from supervisr.core.tasks import debug_progress_task
from supervisr.core.utils import get_reverse_dns
from supervisr.core.views.generic import AdminRequiredMixin, GenericIndexView


class IndexView(TemplateView, AdminRequiredMixin):
    """Admin index"""

    template_name = '_admin/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_count'] = User.objects.all().count() - 1
        context['celery_workers'] = celery.current_app.control.inspect().ping()
        return context


class UserIndexView(GenericIndexView, AdminRequiredMixin):
    """show list of all users"""

    template = '_admin/users.html'
    model = User

    def get_instance(self) -> QuerySet:
        return self.model.objects.all().order_by('date_joined').exclude(pk=get_system_user().pk)


class InfoView(TemplateView, AdminRequiredMixin):
    """Admin Info view"""

    template_name = '_admin/info.html'

    def get_context_data(self, **kwargs):
        """Show system information"""
        context = super().get_context_data(**kwargs)
        request = self.request
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
        results = get_module_info.send(sender=None)
        for handler, mod_info in results:
            # Get the handler's root module
            info_data[handler.__module__] = mod_info
        context['info'] = info_data
        return context


class EventView(GenericIndexView, AdminRequiredMixin):
    """show list of all events"""

    template = '_admin/events.html'
    model = Event

    def get_instance(self) -> QuerySet:
        return self.model.objects.all().order_by('-create_date')


class DebugView(TemplateView, AdminRequiredMixin):
    """Show misc debug buttons"""

    template_name = '_admin/debug.html'

    def post(self, request: HttpRequest) -> HttpResponse:
        """Run actions"""
        if 'raise_error' in request.POST:
            raise RuntimeError('test error')
        elif 'clear_cache' in request.POST:
            cache.clear()
            messages.success(request, _('Successfully cleared Cache'))
        elif 'update_settings' in request.POST:
            setting = Setting.get('domain')
            on_setting_update.send(sender=setting)
            messages.success(request, _('Successfully updated settings.'))
        elif 'start_task' in request.POST:
            seconds = int(request.POST.get('start_task_sec'))
            result = request.user.task_apply_async(debug_progress_task, seconds)
            messages.success(request, _('Started Task, ID: %(id)s' % {'id': result.id}))
        elif 'send_email' in request.POST:
            request.user.task_apply_async(
                send_message,
                recipients=[request.user.email],
                subject=_("Debug"),
                template='email/account_confirm.html')
        return super().get(request)


class FlowerView(TemplateView, AdminRequiredMixin):
    """View to show iframe with flower"""

    template_name = '_admin/flower.html'


class TasksView(GenericIndexView, AdminRequiredMixin):
    """Show list of all tasks and their current status"""

    template_name = '_admin/tasks.html'
    model = Task

    def get_instance(self) -> QuerySet:
        return self.model.objects.all().order_by('-created')
