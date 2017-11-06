# -*- coding: utf-8 -*-
"""
Functions for creating XML output.
"""
from __future__ import absolute_import

import logging

from supervisr.core.utils import render_to_string
from supervisr.mod.auth.saml.idp.xml_signing import (get_signature_xml,
                                                     load_certificate,
                                                     load_private_key,
                                                     sign_with_signxml)

LOGGER = logging.getLogger(__name__)


def _get_attribute_statement(params):
    """
    Inserts AttributeStatement, if we have any attributes.
    Modifies the params dict.
    PRE-REQ: params['SUBJECT'] has already been created (usually by a call to
    _get_subject().
    """
    attributes = params.get('ATTRIBUTES', [])
    if len(attributes) < 1:
        params['ATTRIBUTE_STATEMENT'] = ''
        return
    # Build complete AttributeStatement.
    params['ATTRIBUTE_STATEMENT'] = render_to_string('saml/xml/attributes.xml', {
        'attributes': attributes})

def _get_in_response_to(params):
    """
    Insert InResponseTo if we have a RequestID.
    Modifies the params dict.
    """
    #NOTE: I don't like this. We're mixing templating logic here, but the
    # current design requires this; maybe refactor using better templates, or
    # just bite the bullet and use elementtree to produce the XML; see comments
    # in xml_templates about Canonical XML.
    request_id = params.get('REQUEST_ID', None)
    if request_id:
        params['IN_RESPONSE_TO'] = 'InResponseTo="%s" ' % request_id
    else:
        params['IN_RESPONSE_TO'] = ''

def _get_subject(params):
    """
    Insert Subject.
    Modifies the params dict.
    """
    params['SUBJECT_STATEMENT'] = render_to_string('saml/xml/subject.xml', params)

def get_assertion_xml(template, parameters, signed=False):
    """
    Get XML for Assertion
    """
    # Reset signature.
    params = {}
    params.update(parameters)
    params['ASSERTION_SIGNATURE'] = ''

    _get_in_response_to(params)
    _get_subject(params) # must come before _get_attribute_statement()
    _get_attribute_statement(params)

    unsigned = render_to_string(template, params)
    # LOGGER.debug('Unsigned: %s', unsigned)
    if not signed:
        return unsigned

    # Sign it.
    signature_xml = get_signature_xml()
    params['ASSERTION_SIGNATURE'] = signature_xml
    return render_to_string(template, params)

def get_response_xml(parameters, signed=False, assertion_id=''):
    """
    Returns XML for response, with signatures, if signed is True.
    """
    # Reset signatures.
    params = {}
    params.update(parameters)
    params['RESPONSE_SIGNATURE'] = ''
    _get_in_response_to(params)

    unsigned = render_to_string('saml/xml/response.xml', params)

    # LOGGER.debug('Unsigned: %s', unsigned)
    if not signed:
        return unsigned

    raw_response = render_to_string('saml/xml/response.xml', params)
    # Sign it.
    if signed:
        signature_xml = get_signature_xml()
        params['RESPONSE_SIGNATURE'] = signature_xml
        # LOGGER.debug("Raw response: %s", raw_response)

        signed = sign_with_signxml(
            load_private_key(), raw_response, [load_certificate(True)],
            reference_uri=assertion_id) \
            .decode("utf-8")
        return signed
    return raw_response
