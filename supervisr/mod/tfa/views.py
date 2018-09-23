"""Supervisr 2FA Views"""
from base64 import b32encode
from binascii import unhexlify

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django_otp import login, match_token, user_has_device
from django_otp.decorators import otp_required
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice
from qrcode import make as qr_make
from qrcode.image.svg import SvgPathImage

from supervisr.core.decorators import reauth_required
from supervisr.core.models import Event
from supervisr.core.views.wizards import BaseWizardView
from supervisr.mod.tfa.forms import (TFASetupInitForm, TFASetupStaticForm,
                                     TFAVerifyForm)
from supervisr.mod.tfa.utils import otpauth_url

TFA_SESSION_KEY = 'supervisr_mod_2fa_key'


@login_required
@reauth_required
def index(request: HttpRequest) -> HttpResponse:
    """Show empty index page"""
    return render(request, 'core/generic.html', {
        'text': 'Test 2FA passed'
    })


@login_required
def verify(request: HttpRequest) -> HttpResponse:
    """Verify 2FA Token"""
    if not user_has_device(request.user):
        messages.error(request, _("You don't have 2-Factor Authentication set up."))
    if request.method == 'POST':
        form = TFAVerifyForm(request.POST)
        if form.is_valid():
            device = match_token(request.user, form.cleaned_data.get('code'))
            if device:
                login(request, device)
                messages.success(request, _('Successfully validated 2FA Token.'))
                # Check if there is a next GET parameter and redirect to that
                if 'next' in request.GET:
                    return redirect(request.GET.get('next'))
                # Otherwise just index
                return redirect(reverse('common-index'))
            messages.error(request, _('Invalid 2-Factor Token.'))
    else:
        form = TFAVerifyForm()

    return render(request, 'generic/form_login.html', {
        'form': form,
        'title': _("SSO - Two-factor verification"),
        'primary_action': _("Verify"),
        'extra_links': {
            'account-logout': 'Logout',
        }
    })


@login_required
def user_settings(request: HttpRequest) -> HttpResponse:
    """View for user settings to control 2FA"""
    static = get_object_or_404(StaticDevice, user=request.user, confirmed=True)
    static_tokens = StaticToken.objects.filter(device=static).order_by('token')
    finished_totp_devices = TOTPDevice.objects.filter(user=request.user, confirmed=True)
    finished_static_devices = StaticDevice.objects.filter(user=request.user, confirmed=True)
    state = finished_totp_devices.exists() and finished_static_devices.exists()
    return render(request, 'tfa/user_settings.html', {
        'static_tokens': static_tokens,
        'state': state,
    })


@login_required
@reauth_required
@otp_required
def disable(request: HttpRequest) -> HttpResponse:
    """Disable 2FA for user"""
    # Delete all the devices for user
    static = get_object_or_404(StaticDevice, user=request.user, confirmed=True)
    static_tokens = StaticToken.objects.filter(device=static).order_by('token')
    totp = TOTPDevice.objects.filter(user=request.user, confirmed=True)
    static.delete()
    totp.delete()
    for token in static_tokens:
        token.delete()
    messages.success(request, 'Successfully disabled 2FA')
    # Create event with email notification
    Event.create(
        user=request.user,
        message=_('You disabled 2FA.'),
        current=True,
        request=request,
        send_notification=True)
    return redirect(reverse('common-index'))


# pylint: disable=too-many-ancestors
@method_decorator([login_required, reauth_required], name="dispatch")
class TFASetupView(BaseWizardView):
    """Wizard to create a Mail Account"""

    title = _('Set up 2FA')
    form_list = [TFASetupInitForm, TFASetupStaticForm]

    totp_device = None
    static_device = None
    confirmed = False

    def get_template_names(self):
        if self.steps.current == '1':
            return 'tfa/wizard_setup_static.html'
        return self.template_name

    def handle_request(self, request: HttpRequest):
        # Check if user has 2FA setup already
        finished_totp_devices = TOTPDevice.objects.filter(user=request.user, confirmed=True)
        finished_static_devices = StaticDevice.objects.filter(user=request.user, confirmed=True)
        if finished_totp_devices.exists() or finished_static_devices.exists():
            messages.error(request, _('You already have 2FA enabled!'))
            return redirect(reverse('common-index'))
        # Check if there's an unconfirmed device left to set up
        totp_devices = TOTPDevice.objects.filter(user=request.user, confirmed=False)
        if not totp_devices.exists():
            # Create new TOTPDevice and save it, but not confirm it
            self.totp_device = TOTPDevice(user=request.user, confirmed=False)
            self.totp_device.save()
        else:
            self.totp_device = totp_devices.first()

        # Check if we have a static device already
        static_devices = StaticDevice.objects.filter(user=request.user, confirmed=False)
        if not static_devices.exists():
            # Create new static device and some codes
            self.static_device = StaticDevice(user=request.user, confirmed=False)
            self.static_device.save()
            # Create 9 tokens and save them
            # pylint: disable=unused-variable
            for counter in range(0, 9):
                token = StaticToken(device=self.static_device, token=StaticToken.random_token())
                token.save()
        else:
            self.static_device = static_devices.first()

        # Somehow convert the generated key to base32 for the QR code
        rawkey = unhexlify(self.totp_device.key.encode('ascii'))
        request.session[TFA_SESSION_KEY] = b32encode(rawkey).decode("utf-8")
        return True

    def get_form(self, step=None, data=None, files=None):
        form = super(TFASetupView, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            form.confirmed = self.confirmed
            form.device = self.totp_device
            form.fields['qr_code'].initial = reverse('supervisr_mod_tfa:tfa-qr')
        elif step == '1':
            # This is a bit of a hack, but the 2fa token from step 1 has been checked here
            # And we need to save it, otherwise it's going to fail in render_done
            # and we're going to be redirected to step0
            self.confirmed = True

            tokens = [(x.token, x.token) for x in self.static_device.token_set.all()]
            form.fields['tokens'].choices = tokens
        return form

    def finish(self, *forms):
        # Save device as confirmed
        self.totp_device.confirmed = True
        self.totp_device.save()
        self.static_device.confirmed = True
        self.static_device.save()
        # Create event with email notification
        Event.create(
            user=self.request.user,
            message=_('You activated 2FA.'),
            current=True,
            request=self.request,
            send_notification=True)
        return redirect(reverse('supervisr_mod_tfa:tfa-index'))


@never_cache
@login_required
def qr_code(request: HttpRequest) -> HttpResponse:
    """View returns an SVG image with the OTP token information"""
    # Get the data from the session
    try:
        key = request.session[TFA_SESSION_KEY]
    except KeyError:
        raise Http404()

    url = otpauth_url(accountname=request.user.username, secret=key)
    # Make and return QR code
    img = qr_make(url, image_factory=SvgPathImage)
    resp = HttpResponse(content_type='image/svg+xml; charset=utf-8')
    img.save(resp)
    return resp
