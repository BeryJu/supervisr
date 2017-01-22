"""
Supervisr Core Utils Test
"""

import platform
import socket

from django.test import RequestFactory, TestCase

from ..utils import get_remote_ip, get_reverse_dns


# pylint: disable=duplicate-code
class TestUtils(TestCase):
    """
    Supervisr Core Utils Test
    """

    def setUp(self):
        self.factory = RequestFactory()

    def test_get_remote_ip(self):
        """
        Test get_remote_ip
        """
        req = self.factory.get('/', HTTP_X_FORWARDED_FOR='1.2.3.4')
        self.assertEqual(get_remote_ip(req), '1.2.3.4')
        req2 = self.factory.get('/', REMOTE_ADDR='2.3.4.5')
        self.assertEqual(get_remote_ip(req2), '2.3.4.5')

    def test_get_reverse_dns(self):
        """
        Test get_reverse_dns
        """
        reverse = get_reverse_dns('127.0.0.1')
        if platform.system() == 'Linux':
            self.assertEqual(reverse, 'localhost')
        elif platform.system() == 'Windows':
            self.assertEqual(reverse, socket.getfqdn())
