"""supervisr core provider object tests"""

from supervisr.core.providers.objects import (ProviderObject,
                                              ProviderObjectTranslator,
                                              ProviderResult)
from supervisr.core.utils.tests import TestCase


class TestProviderObjects(TestCase):
    """Test Provider Objects"""

    def test_provider_object(self):
        """Test `ProviderObject`"""
        obj = ProviderObject(None)
        self.assertEqual(obj.save(created=False), ProviderResult.NOT_IMPLEMENTED)
        self.assertEqual(obj.delete(), ProviderResult.NOT_IMPLEMENTED)

    def test_object_translator(self):
        """Test ProviderObjectTranslator"""
        translator = ProviderObjectTranslator(None)
        with self.assertRaises(NotImplementedError):
            translator.to_external(None)
