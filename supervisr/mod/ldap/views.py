"""
Supervisr Mod LDAP Views
"""


from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import Setting
from supervisr.mod.ldap.forms.settings import SettingsForm


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_settings(req, mod):
    """
    Default view for modules without admin view
    """
    initial_data = {
        'enabled':       Setting.get('mod:ldap:enabled') == 'True',
        'host':          Setting.get('mod:ldap:server', None),
        'base':          Setting.get('mod:ldap:base', None),
        'create_base':   Setting.get('mod:ldap:create_base', None),
        'bind_user':     Setting.get('mod:ldap:bind:user', None),
        'bind_password': Setting.get('mod:ldap:bind:pass', None),
        'domain':        Setting.get('mod:ldap:domain', None),
    }
    if req.method == 'POST':
        form = SettingsForm(req.POST)
        if form.is_valid():
            Setting.set('mod:ldap:enabled', form.cleaned_data.get('enabled'))
            Setting.set('mod:ldap:server', form.cleaned_data.get('host'))
            Setting.set('mod:ldap:base', form.cleaned_data.get('base'))
            Setting.set('mod:ldap:create_base', form.cleaned_data.get('create_base'))
            Setting.set('mod:ldap:bind:user', form.cleaned_data.get('bind_user'))
            Setting.set('mod:ldap:bind:pass', form.cleaned_data.get('bind_password'))
            Setting.set('mod:ldap:domain', form.cleaned_data.get('domain'))
            Setting.objects.update()
            messages.success(req, _('Settings successfully updated'))
        return redirect(reverse('ldap:admin_settings', kwargs={'mod': mod}))
    else:
        form = SettingsForm(initial=initial_data)
    return render(req, 'ldap/settings.html', {
        'form': form
        })
