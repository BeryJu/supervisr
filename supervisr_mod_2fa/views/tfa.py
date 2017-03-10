"""
Supervisr 2FA Views
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _
from django_otp import match_token, user_has_device
from django_otp.decorators import otp_required

from supervisr.decorators import reauth_required

from ..forms.tfa import TFAVerifyForm


@otp_required
@login_required
def index(req):
    """
    Show empty index page
    """
    return render(req, 'core/base.html')

@login_required
def verify(req):
    """
    Verify 2FA Token
    """
    if not user_has_device(req.user):
        messages.error(req, _("You don't have 2-Factor Authentication set up."))
    if req.method == 'POST':
        form = TFAVerifyForm(req.POST)
        if form.is_valid():
            dev = match_token(req.user, form.cleaned_data.get('code'))
            if dev:
                # Check if there is a next GET parameter and redirect to that
                if 'next' in req.GET:
                    return redirect(req.GET.get('next'))
                # Otherwise just index
                return redirect(reverse('common-index'))
            else:
                messages.error(req, _('Failed to verify 2-Factor Token'))
    else:
        form = TFAVerifyForm()

    return render(req, 'core/generic_form_login.html', {
        'form': form,
        'title': _("Two-factor authentication code"),
        'primary_action': _("Verify"),
        })

@login_required
@reauth_required
def setup(req):
    """
    Wizard to set up 2FA
    """
    return render(req, 'core/generic.html', {
        'text': 'Test re-auth'
        })
