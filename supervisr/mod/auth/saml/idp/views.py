"""
Supervisr SAML IDP Views
"""
import logging

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import (Http404, HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from OpenSSL.crypto import FILETYPE_PEM
from OpenSSL.crypto import Error as CryptoError
from OpenSSL.crypto import load_certificate

from supervisr.core.models import Event, Setting, UserAcquirableRelationship
from supervisr.core.utils import render_to_string
from supervisr.core.views.common import ErrorResponseView
from supervisr.core.views.settings import GenericSettingView
from supervisr.mod.auth.saml.idp import exceptions, registry, xml_signing
from supervisr.mod.auth.saml.idp.forms.settings import IDPSettingsForm

LOGGER = logging.getLogger(__name__)

# The 'schemes' argument for the URLValidator was introduced in Django 1.6. This
# ensure that URL validation works in 1.5 as well.
try:
    URL_VALIDATOR = URLValidator(schemes=('http', 'https'))
except TypeError:
    URL_VALIDATOR = URLValidator()

BASE_TEMPLATE_DIR = 'saml/idp/'


def _generate_response(request, processor, remote):
    """
    Generate a SAML response using processor and return it in the proper Django
    response.
    """
    try:
        ctx = processor.generate_response()
        ctx['remote'] = remote
    except exceptions.UserNotAuthorized:
        return render(request, 'saml/idp/invalid_user.html')

    return render(request, 'saml/idp/login.html', ctx)


def render_xml(request, template, ctx):
    """
    Render template with content_type application/xml
    """
    return render(request, template, context=ctx, content_type="application/xml")


@csrf_exempt
def login_begin(request):
    """
    Receives a SAML 2.0 AuthnRequest from a Service Provider and
    stores it in the session prior to enforcing login.
    """
    if request.method == 'POST':
        source = request.POST
    else:
        source = request.GET
    # Store these values now, because Django's login cycle won't preserve them.

    try:
        request.session['SAMLRequest'] = source['SAMLRequest']
    except (KeyError, MultiValueDictKeyError):
        return HttpResponseBadRequest('the SAML request payload is missing')

    request.session['RelayState'] = source.get('RelayState', '')
    return redirect(reverse('supervisr_mod_auth_saml_idp:saml_login_process'))


def redirect_to_sp(request, acs_url, saml_response, relay_state):
    """
    Return autosubmit form
    """
    return render(request, 'core/autosubmit_form.html', {
        'url': acs_url,
        'attrs': {
            'SAMLResponse': saml_response,
            'RelayState': relay_state
        }
    })


@login_required
def login_process(request):
    """
    Processor-based login continuation.
    Presents a SAML 2.0 Assertion for POSTing back to the Service Provider.
    """
    LOGGER.debug("Request: %s", request)
    proc, remote = registry.find_processor(request)
    # Check if user has access
    access = True
    if remote.productextensionsaml2_set.exists() and \
            remote.productextensionsaml2_set.first().product_set.exists():
        # Only check if there is a connection from OAuth2 Application to product
        product = remote.productextensionsaml2_set.first().product_set.first()
        relationship = UserAcquirableRelationship.objects.filter(user=request.user, model=product)
        # Product is invite_only = True and no relation with user exists
        if product.invite_only and not relationship.exists():
            access = False
    # Check if we should just autosubmit
    if remote.skip_authorization and access:
        # full_res = _generate_response(request, proc, remote)
        ctx = proc.generate_response()
        # User accepted request
        Event.create(
            user=request.user,
            message=_('You authenticated %s (via SAML) (skipped Authz)' % remote.name),
            request=request,
            current=False,
            hidden=True)
        return redirect_to_sp(
            request=request,
            acs_url=ctx['acs_url'],
            saml_response=ctx['saml_response'],
            relay_state=ctx['relay_state'])
    if request.method == 'POST' and request.POST.get('ACSUrl', None) and access:
        # User accepted request
        Event.create(
            user=request.user,
            message=_('You authenticated %s (via SAML)' % remote.name),
            request=request,
            current=False,
            hidden=True)
        return redirect_to_sp(
            request=request,
            acs_url=request.POST.get('ACSUrl'),
            saml_response=request.POST.get('SAMLResponse'),
            relay_state=request.POST.get('RelayState'))
    else:
        try:
            full_res = _generate_response(request, proc, remote)
            if not access:
                LOGGER.warning("User '%s' has no invitation to '%s'", request.user, product)
                messages.error(request, "You have no access to '%s'" % product.name)
                raise Http404
            return full_res
        except exceptions.CannotHandleAssertion as exc:
            return ErrorResponseView.as_view()(request, str(exc))


@csrf_exempt
def logout(request):
    """
    Allows a non-SAML 2.0 URL to log out the user and
    returns a standard logged-out page. (SalesForce and others use this method,
    though it's technically not SAML 2.0).
    """
    auth.logout(request)

    redirect_url = request.GET.get('redirect_to', '')

    try:
        URL_VALIDATOR(redirect_url)
    except ValidationError:
        pass
    else:
        return HttpResponseRedirect(redirect_url)

    return render(request, 'saml/idp/logged_out.html')


@login_required
@csrf_exempt
def slo_logout(request):
    """
    Receives a SAML 2.0 LogoutRequest from a Service Provider,
    logs out the user and returns a standard logged-out page.
    """
    request.session['SAMLRequest'] = request.POST['SAMLRequest']
    # TODO: Parse SAML LogoutRequest from POST data, similar to login_process().
    # TODO: Add a URL dispatch for this view.
    # TODO: Modify the base processor to handle logouts?
    # TODO: Combine this with login_process(), since they are so very similar?
    # TODO: Format a LogoutResponse and return it to the browser.
    # XXX: For now, simply log out without validating the request.
    auth.logout(request)
    return render(request, 'saml/idp/logged_out.html')


def descriptor(request):
    """
    Replies with the XML Metadata IDSSODescriptor.
    """
    entity_id = Setting.get('issuer')
    slo_url = request.build_absolute_uri(reverse('supervisr_mod_auth_saml_idp:saml_logout'))
    sso_url = request.build_absolute_uri(reverse('supervisr_mod_auth_saml_idp:saml_login_begin'))
    pubkey = xml_signing.load_certificate(strip=True)
    ctx = {
        'entity_id': entity_id,
        'cert_public_key': pubkey,
        'slo_url': slo_url,
        'sso_url': sso_url
    }
    metadata = render_to_string('saml/xml/metadata.xml', ctx)
    response = HttpResponse(metadata, content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename="sv_metadata.xml'
    return response


class IDPSettingsView(GenericSettingView):
    """IDP Settings"""

    form = IDPSettingsForm
    template_name = 'saml/idp/settings.html'

    def dispatch(self, request, *args, **kwargs):
        self.extra_data['metadata'] = escape(descriptor(request).content)

        # Show the certificate fingerprint
        sha1_fingerprint = _('<failed to parse certificate>')
        try:
            cert = load_certificate(FILETYPE_PEM, Setting.get('certificate'))
            sha1_fingerprint = cert.digest("sha1")
        except CryptoError:
            pass
        self.extra_data['fingerprint'] = sha1_fingerprint
        return super(IDPSettingsView, self).dispatch(request, *args, **kwargs)
