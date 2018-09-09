"""supervisr core provider base tests"""

from supervisr.core.providers.base import (BaseProvider, ProviderMetadata,
                                           get_providers)
from supervisr.core.tests.utils import TestCase


class TestProviderBase(TestCase):
    """Test Provider"""

    def test_metadata(self):
        """Test `ProviderMetadata`"""
        meta = ProviderMetadata(self.provider)
        self.assertEqual(meta.get_capabilities(), [])
        self.assertEqual(meta.get_author(), 'BeryJu.org')

    def test_base_provider(self):
        """Test `BaseProvider`"""
        self.assertEqual(self.provider.provider.dotted_path, ('supervisr.mod.provider.debug.'
                                                              'providers.core.DebugProvider'))
        self.assertIsInstance(self.provider.provider.get_meta, ProviderMetadata)
        base_provider = BaseProvider(None)
        self.assertIsNone(base_provider.get_translator(None))

    def test_get_providers(self):
        """Test `get_providers`"""
        providers = get_providers()
        for provider in providers:
            self.assertTrue(issubclass(provider, BaseProvider))
