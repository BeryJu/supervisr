"""supervisr core utils.config tests"""

from django.conf import ImproperlyConfigured

from supervisr.core.utils.config import ConfigLoader
from supervisr.core.utils.tests import TestCase


class TestConfig(TestCase):
    """Test ConfigLoader"""

    def test_load_invalid(self):
        """Test loading of invalid config"""
        cloader = ConfigLoader()
        with self.assertRaises(ImproperlyConfigured):
            cloader.update_from_file('supervisr/environments/invalid.yml')

    def test_with_default(self):
        """Test .default context manager"""
        cloader = ConfigLoader()
        default_value = 'test_default'
        with cloader.default(default_value):
            self.assertEqual(cloader.get('empty_key'), default_value)

    def test_load_dict(self):
        """Test .update_from_dict"""
        cloader = ConfigLoader()
        cloader.update_from_dict({'test': 'value'})
        self.assertIn('test', cloader.raw)
