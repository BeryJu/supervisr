"""
Supervisr SAML IDP Views
"""
import logging
import os

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.shortcuts import redirect, render
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from supervisr.core.models import Setting
from supervisr.core.utils import render_to_string
from supervisr.core.views.common import error_response
from supervisr.mod.auth.saml.idp import exceptions, registry, xml_signing
from supervisr.mod.auth.saml.idp.forms.settings import SettingsForm

LOGGER = logging.getLogger(__name__)

# The 'schemes' argument for the URLValidator was introduced in Django 1.6. This
# ensure that URL validation works in 1.5 as well.
try:
    URL_VALIDATOR = URLValidator(schemes=('http', 'https'))
except TypeError:
    URL_VALIDATOR = URLValidator()

BASE_TEMPLATE_DIR = 'saml/idp/'


def _get_template_names(filename, processor=None):
    """
    Create a list of template names to use based on the processor name. This
    makes it possible to have processor-specific templates.
    """
    specific_templates = []
    if processor and processor.name:
        specific_templates = [
            os.path.join(BASE_TEMPLATE_DIR, processor.name, filename)]

    return specific_templates + [os.path.join(BASE_TEMPLATE_DIR, filename)]


def _generate_response(request, processor):
    """
    Generate a SAML response using processor and return it in the proper Django
    response.
    """
    try:
        ctx = processor.generate_response()
    except exceptions.UserNotAuthorized:
        template_names = _get_template_names('invalid_user.html', processor)
        return render(request, template_names)

    template_names = _get_template_names('login.html', processor)
    return render(request, template_names, ctx)


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
    return redirect(reverse('supervisr/mod/auth/saml/idp:saml_login_process'))

@login_required
def login_process(request):
    """
    Processor-based login continuation.
    Presents a SAML 2.0 Assertion for POSTing back to the Service Provider.
    """
    LOGGER.debug("Request: %s", request)
    try:
        proc = registry.find_processor(request)
        return _generate_response(request, proc)
    except exceptions.CannotHandleAssertion as exc:
        return error_response(request, str(exc))

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
    #TODO: Parse SAML LogoutRequest from POST data, similar to login_process().
    #TODO: Add a URL dispatch for this view.
    #TODO: Modify the base processor to handle logouts?
    #TODO: Combine this with login_process(), since they are so very similar?
    #TODO: Format a LogoutResponse and return it to the browser.
    #XXX: For now, simply log out without validating the request.
    auth.logout(request)
    return render(request, 'saml/idp/logged_out.html')

def descriptor(request):
    """
    Replies with the XML Metadata IDSSODescriptor.
    """
    entity_id = Setting.get('mod:auth:saml:idp:issuer')
    slo_url = request.build_absolute_uri(reverse('supervisr/mod/auth/saml/idp:saml_logout'))
    sso_url = request.build_absolute_uri(reverse('supervisr/mod/auth/saml/idp:saml_login_begin'))
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

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_settings(request, mod):
    """
    Show view with metadata xml
    """
    metadata = descriptor(request).content

    keys = ['issuer', 'certificate', 'private_key', 'signing']
    base = 'mod:auth:saml:idp'
    initial_data = {}
    for key in keys:
        initial_data[key] = Setting.get('%s:%s' % (base, key))
    if request.method == 'POST':
        settings_form = SettingsForm(request.POST)
        print(settings_form.errors)
        if settings_form.is_valid():
            for key in keys:
                Setting.set('%s:%s' % (base, key), settings_form.cleaned_data.get(key))
            Setting.objects.update()
            messages.success(request, _('Settings successfully updated'))
        else:
            messages.error(request, _('Failed to update settings'))
        return redirect(reverse('supervisr/mod/auth/saml/idp:admin_settings', kwargs={'mod': mod}))
    else:
        settings_form = SettingsForm(initial=initial_data)
    return render(request, 'saml/idp/settings.html', {
        'metadata': escape(metadata),
        'mod': mod,
        'settings_form': settings_form
        })
