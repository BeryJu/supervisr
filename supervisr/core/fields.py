"""Supervisr Core Fields"""

import base64
import json

import Crypto.Cipher.AES
from django.conf import settings
from django.db import models
from django.utils.encoding import force_bytes, force_text


class JSONField(models.TextField):
    """Field to save json in DB, works on non-postgres"""

    # pylint: disable=unused-argument
    def from_db_value(self, value, experssion, connection, context):
        """Convert JSON String to object"""
        if value is None:
            return value

        return json.loads(value)

    def to_python(self, value):
        """Convert JSON String to object"""
        if value is None or isinstance(value, JSONField):
            return value

        return json.loads(value)

    def get_prep_value(self, value):
        """Convert back to text"""
        return json.dumps(value)


class SignatureException(Exception):
    """Exception for when decryption fails"""
    pass


class SignedAESEncryption(object):
    """AES sign helper"""
    cipher_class = Crypto.Cipher.AES
    mode = Crypto.Cipher.AES.MODE_SIV
    sign = True
    prefix = 'AES'

    def __init__(self):
        self.init()

    def init(self):
        """(Re-) initialise cipher"""
        self.cipher = self.cipher_class.new(self.get_key(), mode=self.mode)

    def get_key(self):
        """Get key"""
        return force_bytes(settings.SECRET_KEY.zfill(32))[:32]

    def is_encrypted(self, value):
        """Return true if value is encrypted"""
        return force_text(value).startswith(self.prefix)

    def decrypt(self, cypher_text):
        """Decrypt cypher_text"""
        self.init()
        _, cypher, tag = force_text(cypher_text).split('$')
        cypher = base64.b64decode(force_bytes(cypher))
        tag = base64.b64decode(force_bytes(tag))
        return force_text(self.cipher.decrypt_and_verify(cypher, tag))

    def encrypt(self, clear_text):
        """Encrypt clear_text"""
        self.init()
        cypher, tag = self.cipher.encrypt_and_digest(force_bytes(clear_text))
        cypher = force_text(base64.b64encode(cypher))
        tag = force_text(base64.b64encode(tag))
        return '$'.join([force_text(self.prefix), cypher, tag])


class EncryptedField(models.TextField):
    """This code is based on http://www.djangosnippets.org/snippets/1095/ and
    django-fields https://github.com/svetlyak40wt/django-fields"""
    encryption_class = SignedAESEncryption

    def __init__(self, *args, **kwargs):
        self.cipher = self.encryption_class()
        super(EncryptedField, self).__init__(*args, **kwargs)

    # pylint: disable=unused-argument
    def from_db_value(self, value, expression, connection, context):
        """ Read Value from Database """
        if value is None:
            return value
        value = force_bytes(value)
        if self.cipher.is_encrypted(value):
            return force_text(self.cipher.decrypt(value))
        return force_text(value)

    def get_db_prep_value(self, value, connection=None, prepared=False):
        """ Prepare value for database   """
        if self.null:
            # Normalize empty values to None
            value = value or None
        if value is None:
            return None
        value = force_bytes(value)
        if not self.cipher.is_encrypted(value):
            value = self.cipher.encrypt(value)
        return force_text(value)
