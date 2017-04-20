"""
Supervisr Mail ServerTest Imap4
"""

import unittest
from imaplib import IMAP4


class TestImap4(unittest.TestCase):

    def setUp(self, server):
        self.client = IMAP4(host=server.fqdn, port=server.imap_port)

    def test_connection(self):
        self.assertTrue(self.client.noop(), True)
