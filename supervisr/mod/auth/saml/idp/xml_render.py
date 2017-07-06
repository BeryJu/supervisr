# -*- coding: utf-8 -*-
"""
Functions for creating XML output.
"""
from __future__ import absolute_import

import logging

from supervisr.core.utils import render_to_string
from supervisr.mod.auth.saml.idp.xml_signing import get_signature_xml

LOGGER = logging.getLogger(__name__)


def _get_attribute_statement(params):
    """
    Inserts AttributeStatement, if we have any attributes.
    Modifies the params dict.
    PRE-REQ: params['SUBJECT'] has already been created (usually by a call to
    _get_subject().
    """
    attributes = params.get('ATTRIBUTES', {})
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

def _get_assertion_xml(template, parameters, signed=False):
    # Reset signature.
    params = {}
    params.update(parameters)
    params['ASSERTION_SIGNATURE'] = ''

    _get_in_response_to(params)
    _get_subject(params) # must come before _get_attribute_statement()
    _get_attribute_statement(params)

    unsigned = render_to_string(template, params)
    LOGGER.debug('Unsigned: %s', unsigned)
    if not signed:
        return unsigned

    # Sign it.
    signature_xml = get_signature_xml(unsigned, params['ASSERTION_ID'])
    params['ASSERTION_SIGNATURE'] = signature_xml
    signed = render_to_string(template, params)

    LOGGER.debug('Signed: %s', signed)
    return signed

def get_assertion_googleapps_xml(parameters, signed=False):
    """
    Get Assertion XML for Google Apps
    """
    return _get_assertion_xml('saml/xml/assertions/google_apps.xml', parameters, signed)

def get_assertion_salesforce_xml(parameters, signed=False):
    """
    Get Assertion XML for Salesforce
    """
    return _get_assertion_xml('saml/xml/assertions/salesforce.xml', parameters, signed)

def get_assertion_generic_xml(parameters, signed=True):
    """
    Get Assertion XML for Generic
    """
    return _get_assertion_xml('saml/xml/assertions/generic.xml', parameters, signed)

def get_response_xml(parameters, signed=False):
    """
    Returns XML for response, with signatures, if signed is True.
    """
    # Reset signatures.
    params = {}
    params.update(parameters)
    params['RESPONSE_SIGNATURE'] = ''
    _get_in_response_to(params)

    unsigned = render_to_string('saml/xml/response.xml', params)

    LOGGER.debug('Unsigned: %s', unsigned)
    if not signed:
        return unsigned

    # Sign it.
    signature_xml = get_signature_xml(unsigned, params['RESPONSE_ID'])
    params['RESPONSE_SIGNATURE'] = signature_xml
    signed = render_to_string('saml/xml/response.xml', params)

    LOGGER.debug('Signed: %s', signed)
    return signed
