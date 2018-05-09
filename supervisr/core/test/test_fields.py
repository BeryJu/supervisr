"""Supervisr core field test"""
import random
import string

from supervisr.core.fields import SignedAESEncryption
from supervisr.core.test.utils import TestCase


class FieldsTest(TestCase):
    """Test Fields"""

    def test_signed_aes_encryption(self):
        """Test SignedAESEncryption"""
        input_string = ''.join(random.choice(string.ascii_uppercase + string.digits)
                               for _ in range(10))
        aes = SignedAESEncryption()
        encrypted = aes.encrypt(input_string)
        self.assertFalse(aes.is_encrypted(input_string))
        self.assertTrue(aes.is_encrypted(encrypted))
        self.assertEqual(aes.decrypt(encrypted), input_string)
