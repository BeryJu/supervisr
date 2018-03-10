"""
Supervisr Mod Influx Views
"""


from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import Setting
from supervisr.mod.stats.influx.forms.settings import SettingsForm
from supervisr.mod.stats.influx.influx_client import InfluxClient


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_settings(request: HttpRequest) -> HttpResponse:
    """Default view for modules without admin view"""
    initial_data = {
        'enabled': Setting.get_bool('enabled'),
        'host': Setting.get('host'),
        'port': Setting.get('port'),
        'database': Setting.get('database'),
        'username': Setting.get('username'),
        'password': Setting.get('password'),
    }
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid() and 'test' not in request.POST:
            for key in ['enabled', 'host', 'port', 'database', 'username', 'password']:
                Setting.set(key, form.cleaned_data.get(key))
            Setting.objects.update()
            messages.success(request, _('Settings successfully updated'))
        elif 'test' in request.POST:
            # Test button that sends a test message
            with InfluxClient() as client:
                client.write("test", 128)
            messages.success(request, _('Successfully Sent test message'))
        return redirect(reverse('supervisr_mod_stats_influx:admin_settings'))
    else:
        form = SettingsForm(initial=initial_data)
    return render(request, 'stats/influx/settings.html', {
        'form': form
    })
