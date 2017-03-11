"""
Supervisr 2FA Views
"""
from base64 import b32encode
from binascii import unhexlify

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django_otp import match_token, user_has_device
from django_otp.plugins.otp_totp.models import TOTPDevice
from qrcode import make as qr_make
from qrcode.image.svg import SvgPathImage

from supervisr.decorators import reauth_required
from supervisr.views.wizard import BaseWizardView

from ..forms.tfa import TFASetupInitForm, TFAVerifyForm
from ..utils import otpauth_url


# @otp_required
@login_required
@reauth_required
def index(req):
    """
    Show empty index page
    """
    return render(req, 'core/generic.html', {
        'text': 'Test 2FA passed'
        })

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

# pylint: disable=too-many-ancestors
@method_decorator([login_required, reauth_required], name="dispatch")
class TFASetupView(BaseWizardView):
    """
    Wizard to create a Mail Account
    """

    title = _('Set up 2FA')
    form_list = [TFASetupInitForm]

    totp_device = None

    def handle_request(self, req):
        if not self.totp_device:
            # Create new TOTPDevice and save it, but not confirm it
            self.totp_device = TOTPDevice(user=req.user, confirmed=False)
            self.totp_device.save()
            # Somehow convert the generated key to base32 for the QR code
            rawkey = unhexlify(self.totp_device.key.encode('ascii'))
            req.session['supervisr_mod_2fa_key'] = b32encode(rawkey).decode("utf-8")

    def get_form(self, step=None, data=None, files=None):
        form = super(TFASetupView, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            form.fields['qr_code'].initial = reverse('supervisr_mod_2fa:tfa-qr')
        return form

    # def done(self, form_dict, **kwargs):
    #     return render(self.request, 'core/generic.html', {
    #         'text': 'Test 2FA passed'
    #         })

@never_cache
@login_required
def qr_code(req):
    """
    View returns an SVG image with the OTP token information
    """
    # Get the data from the session
    try:
        key = req.session['supervisr_mod_2fa_key']
    except KeyError:
        raise Http404()

    url = otpauth_url(accountname=req.user.username, secret=key)
    print(url)
    # Make and return QR code
    img = qr_make(url, image_factory=SvgPathImage)
    resp = HttpResponse(content_type='image/svg+xml; charset=utf-8')
    img.save(resp)
    return resp
