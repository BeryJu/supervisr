# -*- coding: utf-8 -*-
"""
Signing code goes here.
"""
from __future__ import absolute_import

import hashlib
import logging
import string

import rsa

from supervisr.mod.saml.idp import saml2idp_metadata as smd
from supervisr.mod.saml.idp.codex import nice64
from supervisr.mod.saml.idp.xml_templates import SIGNATURE, SIGNED_INFO

logger = logging.getLogger(__name__)

def load_certificate(config):
    if smd.CERTIFICATE_DATA in config:
        return config.get(smd.CERTIFICATE_DATA, '')

    certificate_filename = config.get(smd.CERTIFICATE_FILENAME)
    logger.info('Using certificate file: ' + certificate_filename)

def load_private_key(config):
    private_key_data = config.get(smd.PRIVATE_KEY_DATA)

    if private_key_data:
        return config.get(smd.PRIVATE_KEY_DATA)

    private_key_file = config.get(smd.PRIVATE_KEY_FILENAME)
    logger.info('Using private key file: {}'.format(private_key_file))


def sign_with_rsa(private_key, data):

    key = rsa.PrivateKey.load_pkcs1(private_key)
    return nice64(rsa.sign(data.encode('utf-8'), key, 'SHA-1'))


def get_signature_xml(subject, reference_uri):
    """
    Returns XML Signature for subject.
    """
    logger.debug('get_signature_xml - Begin.')
    config = smd.SAML2IDP_CONFIG

    private_key = load_private_key(config)
    certificate = load_certificate(config)

    logger.debug('Subject: ' + subject)
    import base64
    # Hash the subject.
    subject_hash = hashlib.sha1()
    subject_hash.update(subject.encode('utf-8'))
    subject_digest = nice64(subject_hash.digest())
    logger.debug('Subject digest: ' + subject_digest)

    # Create signed_info.
    signed_info = string.Template(SIGNED_INFO).substitute({
        'REFERENCE_URI': reference_uri,
        'SUBJECT_DIGEST': subject_digest,
        })
    logger.debug('SignedInfo XML: ' + signed_info)

    rsa_signature = sign_with_rsa(private_key, signed_info)
    logger.debug('RSA Signature: ' + rsa_signature)

    # Put the signed_info and rsa_signature into the XML signature.
    signed_info_short = signed_info.replace(' xmlns:ds="http://www.w3.org/2000/09/xmldsig#"', '')
    signature_xml = string.Template(SIGNATURE).substitute({
        'RSA_SIGNATURE': rsa_signature,
        'SIGNED_INFO': signed_info_short,
        'CERTIFICATE': certificate,
        })
    logger.info('Signature XML: ' + signature_xml)
    return signature_xml
