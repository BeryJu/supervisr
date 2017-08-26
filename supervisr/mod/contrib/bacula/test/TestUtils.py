"""
Supervisr Bacula Utils Test
"""

from unittest import skipUnless

from django.conf import settings
from django.test import RequestFactory, TestCase

from supervisr.mod.contrib.bacula.utils import db_size, size_human


class TestUtils(TestCase):
    """
    Supervisr Bacula Utils Test
    """

    def setUp(self):
        self.factory = RequestFactory()

    def test_size_human(self):
        """
        Test size_human
        """
        self.assertEqual(size_human(None), 0)
        self.assertEqual(size_human(0), '0 bytes')
        self.assertEqual(size_human(1), '1 byte')
        self.assertEqual(size_human(10000), '10 kB')

    @skipUnless('mysql' in settings.DATABASES['default']['ENGINE'],
                "only supported in mysql")
    def test_db_size(self):
        """
        test db_size
        """
        self.assertNotEqual(db_size('default'), 0)
