"""Supervisr Core Django Admin Test"""

from django.test import TestCase

from supervisr.core.admin import admin_autoregister


class TestDjangoAdmin(TestCase):
    """Supervisr Core Django Admin Test"""

    def setUp(self):
        pass

    def test_autoregister(self):
        """Test Admin autoregister"""
        admin_autoregister('supervisr_core')
