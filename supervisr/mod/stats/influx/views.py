"""
Supervisr Mod Influx Views
"""


from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import Setting
from supervisr.mod.stats.influx.forms.settings import SettingsForm
from supervisr.mod.stats.influx.influx_client import InfluxClient


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_settings(req, mod):
    """
    Default view for modules without admin view
    """
    initial_data = {
        'enabled': Setting.get_bool('enabled'),
        'host': Setting.get('host'),
        'port': Setting.get('port'),
        'database': Setting.get('database'),
        'username': Setting.get('username'),
        'password': Setting.get('password'),
    }
    if req.method == 'POST':
        form = SettingsForm(req.POST)
        if form.is_valid() and 'test' not in req.POST:
            print(form.cleaned_data)
            for key in ['enabled', 'host', 'port', 'database', 'username', 'password']:
                Setting.set(key, form.cleaned_data.get(key))
            Setting.objects.update()
            messages.success(req, _('Settings successfully updated'))
        elif 'test' in req.POST:
            # Test button that sends a test message
            with InfluxClient() as client:
                client.write("test", 128)
            messages.success(req, _('Successfully Sent test message'))
        return redirect(reverse('supervisr/mod/stats/influx:admin_settings', kwargs={'mod': mod}))
    else:
        form = SettingsForm(initial=initial_data)
    return render(req, 'stats/influx/settings.html', {
        'form': form
        })
