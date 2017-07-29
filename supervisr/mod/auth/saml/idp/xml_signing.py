# -*- coding: utf-8 -*-
"""
Signing code goes here.
"""
from __future__ import absolute_import

import logging

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from lxml import etree
from signxml import XMLSigner
from signxml.util import strip_pem_header

from supervisr.core.utils import render_to_string
from supervisr.mod.auth.saml.idp import saml2idp_metadata as smd

LOGGER = logging.getLogger(__name__)

def load_certificate(config, strip=True):
    """
    Get Public key from config
    """
    if smd.CERTIFICATE_DATA in config:
        if strip:
            return strip_pem_header(config.get(smd.CERTIFICATE_DATA, '')).replace('\n', '')
        return config.get(smd.CERTIFICATE_DATA, '')

def load_private_key(config):
    """
    Get Private Key from config
    """
    if smd.PRIVATE_KEY_DATA in config:
        return config.get(smd.PRIVATE_KEY_DATA)

def sign_with_signxml(private_key, data, cert, reference_uri=None):
    """
    Sign Data with signxml
    """
    key = serialization.load_pem_private_key(
        str.encode('\n'.join([x.strip() for x in private_key.split('\n')])),
        password=None, backend=default_backend())
    # pylint: disable=no-member
    root = etree.fromstring(data)
    signer = XMLSigner(c14n_algorithm='http://www.w3.org/2001/10/xml-exc-c14n#')
    # pylint: disable=no-member
    return etree.tostring(signer.sign(root, key=key, cert=cert, reference_uri=reference_uri))

def get_signature_xml():
    """
    Returns XML Signature for subject.
    """
    return render_to_string('saml/xml/signature.xml', {})
