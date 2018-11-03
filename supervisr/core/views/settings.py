"""supervisr settings views"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

from supervisr.core.forms.settings import SettingsForm
from supervisr.core.models import Setting
from supervisr.core.views.generic import AdminRequiredMixin


@login_required
@user_passes_test(lambda u: u.is_superuser)
def settings(request: HttpRequest, namespace: str) -> HttpResponse:
    """Admin settings"""
    all_settings = Setting.objects.filter(namespace=namespace).order_by('key')
    namespaces = Setting.objects.all() \
        .values_list('namespace', flat=True) \
        .distinct() \
        .order_by('namespace')
    # Update settings when posted
    if request.method == 'POST':
        update_counter = 0
        for name_key, value in request.POST.items():
            # Names are formatted <namespace>/<key>
            if '/' in name_key:
                namespace, key = name_key.split('/')
                settings = Setting.objects.filter(namespace=namespace, key=key)
                if not settings.exists():
                    continue
                setting = settings.first()
                if value != setting.value:
                    update_counter += 1
                    setting.value = value
                    setting.save()
        Setting.objects.update()
        messages.success(request, _('Updated %d settings' % update_counter))
    return render(request, '_admin/settings.html', {
        'settings': all_settings,
        'namespaces': namespaces,
        'current_namespace': namespace
    })


class ModuleDefaultView(TemplateView, AdminRequiredMixin):
    """Default view for modules without admin view"""

    template_name = '_admin/module_default.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module'] = self.request.GET.get('module', '')
        return context


class GenericSettingView(LoginRequiredMixin, AdminRequiredMixin):
    """Generic Setting View"""

    form = None  # type: Type[SettingsForm]
    template_name = 'generic/form.html'  # type: str
    extra_data = {}

    def render(self, request: HttpRequest, form: SettingsForm) -> HttpResponse:
        """Render our template

        Args:
            request: The current request

        Returns:
            Login template
        """
        self.extra_data.update({'form': form})
        return render(request, self.template_name, self.extra_data)

    def get(self, request: HttpRequest) -> HttpResponse:
        """Handle Get request

        Args:
            request: The current request

        Returns:
            Login template
        """
        form = self.form()  # pylint: disable=not-callable
        return self.render(request, form)

    def post(self, request: HttpRequest) -> HttpResponse:
        """Handle Post request

        Args:
            request: The current request

        Returns:
            Either a redirect to next view or login template if any errors exist
        """
        form = self.form(request.POST)  # pylint: disable=not-callable
        if form.is_valid():
            form.save()
            messages.success(request, _('Settings successfully updated.'))
        return self.render(request, form=form)
