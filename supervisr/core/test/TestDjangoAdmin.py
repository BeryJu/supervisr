"""
Supervisr Core Django Admin Test
"""

from django.test import TestCase

from ..admin import admin_autoregister


class TestDjangoAdmin(TestCase):
    """
    Supervisr Core Django Admin Test
    """

    def setUp(self):
        pass

    # pylint: disable=no-self-use
    def test_autoregister(self):
        """
        Test Admin autoregister
        """
        admin_autoregister('core')
