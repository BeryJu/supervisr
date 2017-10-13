"""
Supervisr Mod LDAP Views
"""


from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import Setting
from supervisr.mod.auth.ldap.forms.settings import SettingsForm


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_settings(req, mod):
    """
    Default view for modules without admin view
    """
    initial_data = {
        'enabled':       Setting.get('enabled') == 'True',
        'host':          Setting.get('server', default=None),
        'base':          Setting.get('base', default=None),
        'create_base':   Setting.get('create_base', default=None),
        'bind_user':     Setting.get('bind:user', default=None),
        'bind_password': Setting.get('bind:password', default=None),
        'domain':        Setting.get('domain', default=None),
    }
    if req.method == 'POST':
        form = SettingsForm(req.POST)
        if form.is_valid():
            Setting.set('enabled', form.cleaned_data.get('enabled'))
            Setting.set('server', form.cleaned_data.get('host'))
            Setting.set('base', form.cleaned_data.get('base'))
            Setting.set('create_base', form.cleaned_data.get('create_base'))
            Setting.set('bind:user', form.cleaned_data.get('bind_user'))
            Setting.set('bind:password', form.cleaned_data.get('bind_password'))
            Setting.set('domain', form.cleaned_data.get('domain'))
            Setting.objects.update()
            messages.success(req, _('Settings successfully updated'))
        return redirect(reverse('supervisr/mod/auth/ldap:admin_settings', kwargs={'mod': mod}))
    else:
        form = SettingsForm(initial=initial_data)
    return render(req, 'ldap/settings.html', {
        'form': form
        })
