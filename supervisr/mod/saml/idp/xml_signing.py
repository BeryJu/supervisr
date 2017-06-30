# -*- coding: utf-8 -*-
"""
Signing code goes here.
"""
from __future__ import absolute_import

import hashlib
import logging

import rsa

from supervisr.core.utils import render_to_string
from supervisr.mod.saml.idp import saml2idp_metadata as smd
from supervisr.mod.saml.idp.codex import nice64

LOGGER = logging.getLogger(__name__)

def load_certificate(config):
    """
    Get Public key from config
    """
    if smd.CERTIFICATE_DATA in config:
        return oneline_cert(config.get(smd.CERTIFICATE_DATA, ''))

def load_private_key(config):
    """
    Get Private Key from config
    """
    if smd.PRIVATE_KEY_DATA in config:
        return config.get(smd.PRIVATE_KEY_DATA)

def sign_with_rsa(private_key, data, _hash='SHA-1'):
    """
    Sign data with private_key
    """
    key = rsa.PrivateKey.load_pkcs1(private_key)
    return nice64(rsa.sign(data.encode('utf-8'), key, _hash))

def oneline_cert(cert):
    """
    Convert a multiline PEM cert into a single line
    """
    lines = cert.split('\n')[1:-1] # remove ----BEGIN CERTIFICATE----- etc
    return ''.join(map(str.strip, lines)) # Also remove space from every line

def get_signature_xml(subject, reference_uri):
    """
    Returns XML Signature for subject.
    """
    LOGGER.debug('get_signature_xml - Begin.')
    config = smd.SAML2IDP_CONFIG

    private_key = load_private_key(config)
    certificate = load_certificate(config)

    LOGGER.debug('Subject: %s', subject)

    # Hash the subject.
    subject_hash = hashlib.sha1()
    subject_hash.update(subject.encode('utf-8'))
    subject_digest = nice64(subject_hash.digest())
    LOGGER.debug('Subject digest: %s', subject_digest)

    # Create signed_info.
    signed_info = render_to_string('saml/xml/signed_info.xml', {
        'REFERENCE_URI': reference_uri,
        'SUBJECT_DIGEST': subject_digest,
        })
    LOGGER.debug('SignedInfo XML: %s', signed_info)

    rsa_signature = sign_with_rsa(private_key, signed_info)
    LOGGER.debug('RSA Signature: %s', rsa_signature)

    # Put the signed_info and rsa_signature into the XML signature.
    signed_info_short = signed_info.replace(' xmlns:ds="http://www.w3.org/2000/09/xmldsig#"', '')
    signature_data = {
        'rsa_signature': rsa_signature,
        'signed_info': signed_info_short,
        'certificate': certificate,
        }
    LOGGER.info('Signature Data: %s', signature_data)
    return signature_data
