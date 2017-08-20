"""
Supervisr Mod Graphite Views
"""


from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import Setting
from supervisr.mod.stats.graphite.forms.settings import SettingsForm
from supervisr.mod.stats.graphite.graphite_client import GraphiteClient


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_settings(req, mod):
    """
    Default view for modules without admin view
    """
    initial_data = {
        'host': Setting.get('host'),
        'port': Setting.get('port'),
        'prefix': Setting.get('prefix'),
        'enabled': Setting.get('enabled'),
    }
    if req.method == 'POST':
        form = SettingsForm(req.POST)
        if form.is_valid() and 'test' not in req.POST:
            Setting.set('host', form.cleaned_data.get('host'))
            Setting.set('port', form.cleaned_data.get('port'))
            Setting.set('prefix', form.cleaned_data.get('prefix'))
            Setting.set('enabled', form.cleaned_data.get('enabled'))
            Setting.objects.update()
            messages.success(req, _('Settings successfully updated'))
        elif 'test' in req.POST:
            # Test button that sends a test message
            with GraphiteClient() as client:
                client.write("test", 128)
            messages.success(req, _('Successfully Sent test message'))
        return redirect(reverse('supervisr/mod/stats/graphite:admin_settings', kwargs={'mod': mod}))
    else:
        form = SettingsForm(initial=initial_data)
    return render(req, 'stats/graphite/settings.html', {
        'form': form
        })
