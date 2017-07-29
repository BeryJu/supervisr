# -*- coding: utf-8 -*-
"""
Signing code goes here.
"""
from __future__ import absolute_import

import base64
import hashlib
import logging

import rsa

from supervisr.core.utils import render_to_string
from supervisr.mod.auth.saml.idp import saml2idp_metadata as smd
from supervisr.mod.auth.saml.idp.codex import nice64

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
    signed = rsa.sign(data.encode('utf-8'), key, _hash)
    return nice64(signed)

def sign_with_crypt(private_key, data):
    import sys
    import crypto
    sys.modules['Crypto'] = crypto
    from Crypto.PublicKey import RSA
    from Crypto.Signature import PKCS1_v1_5
    from Crypto.Hash import SHA

    message = 'To be signed'
    key = RSA.importKey(private_key)
    h = SHA.new(message.encode('utf-8'))
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(h)

    return nice64(signature)

def sign_with_signxml(private_key, data, cert):
    from lxml import etree
    from base64 import b64decode
    from signxml import XMLSigner
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    key = serialization.load_pem_private_key(str.encode('\n'.join([x.strip() for x in private_key.split('\n')])), password=None, backend=default_backend())
    root = etree.fromstring(data)
    signer = XMLSigner(signature_algorithm='rsa-sha1', digest_algorithm='sha1')
    return etree.tostring(signer.sign(root, key=key, cert=cert))

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

    # rsa_signature = sign_xml(signed_info, private_key, certificate)
    rsa_signature = sign_with_rsa(private_key, signed_info)
    print(rsa_signature)
    print("\n\n\n")
    rsa_signature = sign_with_crypt(private_key, signed_info)
    print(rsa_signature)
    print("\n\n\n")
    signed_info = sign_with_signxml(private_key, signed_info, certificate)
    print(signed_info)
    LOGGER.debug('RSA Signature: %s', rsa_signature)

    # Put the signed_info and rsa_signature into the XML signature.
    signed_info_short = signed_info.decode('utf-8').replace(' xmlns:ds="http://www.w3.org/2000/09/xmldsig#"', '')
    signature_data = {
        'RSA_SIGNATURE': rsa_signature,
        'SIGNED_INFO': signed_info_short,
        'CERTIFICATE': certificate,
        }
    LOGGER.info('Signature Data: %s', signature_data)
    return render_to_string('saml/xml/signature.xml', signature_data)
