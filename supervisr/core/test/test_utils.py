"""
Supervisr Core Utils Test
"""

import socket
import sys
from unittest import skipUnless

from django.http import HttpResponseServerError
from django.test import RequestFactory, TestCase

from supervisr.core.test.utils import test_request
from supervisr.core.utils import (b64decode, b64encode, check_db_connection,
                                  class_to_path, do_404, get_remote_ip,
                                  get_reverse_dns, path_to_class,
                                  render_to_string, uuid)


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
        request = self.factory.get('/', HTTP_X_FORWARDED_FOR='1.2.3.4')
        self.assertEqual(get_remote_ip(request), '1.2.3.4')
        request2 = self.factory.get('/', REMOTE_ADDR='2.3.4.5')
        self.assertEqual(get_remote_ip(request2), '2.3.4.5')

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
        self.assertIsInstance(test_request(lambda x: x, method='invalid'), HttpResponseServerError)

    def test_uuid(self):
        """
        test uuid
        """
        self.assertTrue(uuid().isalnum())

    def test_404(self):
        """
        test 404 helper
        """
        request = self.factory.get('/')
        self.assertEqual(do_404(request).status_code, 404)

    def test_render_to_string(self):
        """
        test render_to_string
        """
        self.assertTrue(render_to_string('email/base.html', {}))

    def test_chck_db_con(self):
        """Test check_db_connection"""
        self.assertTrue(check_db_connection('default'))
        self.assertFalse(check_db_connection('invalid'))

    def test_class_path(self):
        """Test class_to_path and path_to_class"""
        self.assertEqual(class_to_path(TestUtils), 'supervisr.core.test.test_utils.TestUtils')
        self.assertEqual(path_to_class(''), None)

    def test_b64(self):
        """Test b64encode and b64decode"""
        tstring = uuid()
        self.assertEqual(b64decode(b64encode(tstring)), tstring)
