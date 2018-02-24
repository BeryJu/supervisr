"""supervisr settings views"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views import View

from supervisr.core.forms.settings import SettingsForm
from supervisr.core.models import Setting


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

@login_required
@user_passes_test(lambda u: u.is_superuser)
def mod_default(request: HttpRequest) -> HttpResponse:
    """Default view for modules without admin view"""
    return render(request, '_admin/mod_default.html', {'mod': request.GET.get('mod', '')})

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class GenericSettingView(View):
    """Generic Setting View"""

    form = None # type: Type[SettingsForm]
    template_name = 'core/generic_form.html' # type: str
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
        form = self.form() # pylint: disable=not-callable
        return self.render(request, form)

    def post(self, request: HttpRequest) -> HttpResponse:
        """Handle Post request

        Args:
            request: The current request

        Returns:
            Either a redirect to next view or login template if any errors exist
        """
        form = self.form(request.POST) # pylint: disable=not-callable
        if form.is_valid():
            form.save()
            messages.success(request, _('Settings successfully updated.'))
        return self.render(request, form=form)
