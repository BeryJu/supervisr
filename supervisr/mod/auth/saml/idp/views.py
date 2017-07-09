"""
Supervisr SAML IDP Views
"""
import logging
import os

from django.contrib import auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template import loader
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt

from supervisr.mod.auth.saml.idp import (exceptions, metadata, registry,
                                         saml2idp_metadata, xml_signing)

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
    return redirect(reverse('idp:saml_login_process'))


@login_required
def login_init(request, resource, **kwargs):
    """
    Initiates an IdP-initiated link to a simple SP resource/target URL.
    """
    name, sp_config = metadata.get_config_for_resource(resource)
    proc = registry.get_processor(name, sp_config)

    try:
        linkdict = dict(metadata.get_links(sp_config))
        pattern = linkdict[resource]
    except KeyError:
        raise ImproperlyConfigured(
            'Cannot find link resource in SAML2IDP_REMOTE setting: "%s"' % resource)
    is_simple_link = ('/' not in resource)
    if is_simple_link:
        simple_target = kwargs['target']
        url = pattern % simple_target
    else:
        url = pattern % kwargs
    proc.init_deep_link(request, sp_config, url)
    return _generate_response(request, proc)


@login_required
def login_process(request):
    """
    Processor-based login continuation.
    Presents a SAML 2.0 Assertion for POSTing back to the Service Provider.
    """
    LOGGER.debug("Request: %s", request)
    proc = registry.find_processor(request)
    return _generate_response(request, proc)

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
    idp_config = saml2idp_metadata.SAML2IDP_CONFIG
    entity_id = idp_config['issuer']
    slo_url = request.build_absolute_uri(reverse('idp:saml_logout'))
    sso_url = request.build_absolute_uri(reverse('idp:saml_login_begin'))
    pubkey = xml_signing.load_certificate(idp_config)
    ctx = {
        'entity_id': entity_id,
        'cert_public_key': pubkey,
        'slo_url': slo_url,
        'sso_url': sso_url
    }
    return render_xml(request, 'saml/xml/metadata.xml', ctx)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_settings(req, mod):
    """
    Show view with metadata xml
    """
    idp_config = saml2idp_metadata.SAML2IDP_CONFIG
    entity_id = idp_config['issuer']
    slo_url = req.build_absolute_uri(reverse('idp:saml_logout'))
    sso_url = req.build_absolute_uri(reverse('idp:saml_login_begin'))
    pubkey = xml_signing.load_certificate(idp_config)
    ctx = {
        'entity_id': entity_id,
        'cert_public_key': pubkey,
        'slo_url': slo_url,
        'sso_url': sso_url
    }
    template = loader.get_template('saml/xml/metadata.xml')

    metadata = template.render(ctx)
    return render(req, 'saml/idp/settings.html', {
        'metadata': escape(metadata),
        'mod': mod
        })