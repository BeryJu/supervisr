"""supervisr mod beacon views"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

from supervisr.mod.beacon.forms import BeaconSettingsForm
from supervisr.mod.beacon.models import Pulse, PulseModule
from supervisr.mod.beacon.sender import Sender


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_settings(request: HttpRequest) -> HttpResponse:
    """Default view for modules without admin view"""
    is_master = len(Pulse.objects.all()) > 0 or settings.DEBUG
    if request.method == 'POST':
        form = BeaconSettingsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Settings successfully updated'))
        return redirect(reverse('supervisr_mod_beacon:admin_settings'))
    else:
        form = BeaconSettingsForm()
    return render(request, 'beacon/settings.html', {
        'form': form,
        'is_master': is_master,
        'installs': Pulse.objects.all(),
        'modules': PulseModule.objects.all()
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def pulse(request: HttpRequest) -> HttpResponse:
    """Send pulse now"""
    sender = Sender()
    sender.tick()
    messages.success(request, _('Successfully pulsed.'))
    return redirect(reverse('supervisr_mod_beacon:admin_settings'))
