"""
Supervisr Core Utils Test
"""

import socket
import sys
from unittest import skipUnless

from django.test import RequestFactory, TestCase

from ..utils import (do_404, get_remote_ip, get_reverse_dns, render_to_string,
                     send_admin_mail, uuid)
from .utils import test_request


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

    @skipUnless(sys.platform.startswith('win'), 'requires Windows')
    def test_reverse_dns_win(self): # pragma: no cover
        """
        Test reverse_dns (windows)
        """
        reverse = get_reverse_dns('127.0.0.1')
        self.assertEqual(reverse, socket.getfqdn())

    @skipUnless(sys.platform.endswith('nix'), 'requires Linux')
    def test_reverse_dns_nix(self): # pragma: no cover
        """
        Test reverse_dns (nix)
        """
        reverse = get_reverse_dns('127.0.0.1')
        self.assertEqual(reverse, 'localhost')

    def test_request_wrong_mtd(self):
        """
        test test_request with a wrong method
        """
        self.assertEqual(test_request(lambda x: x, method='invalid'), None)

    def test_uuid(self):
        """
        test uuid
        """
        self.assertTrue(uuid().isalnum())

    def test_404(self):
        """
        test 404 helper
        """
        req = self.factory.get('/')
        self.assertEqual(do_404(req).status_code, 404)

    def test_send_admin_mail(self):
        """
        test send_admin_mail
        """
        self.assertTrue(send_admin_mail(None, 'test'), True)

    def test_render_to_string(self):
        """
        test render_to_string
        """
        self.assertTrue(render_to_string('core/base_email.html', {}))
