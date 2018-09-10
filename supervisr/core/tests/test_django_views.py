"""Supervisr Core Django Admin Test"""

from supervisr.core.admin import admin_autoregister
from supervisr.core.utils.tests import TestCase


class TestDjangoAdmin(TestCase):
    """Supervisr Core Django Admin Test"""

    def test_autoregister(self):
        """Test Admin autoregister"""
        admin_autoregister('supervisr_core')
