"""
Supervisr Mail ServerTest Smtp
"""

import unittest
from smtplib import SMTP

from supervisr.core.models import Domain

from supervisr.mail.models import MailAccount, MailDomain


class TestSmtp(unittest.TestCase):

    def setUp(self):
        self.client = SMTP(host='mx1debug.s.beryju.org', port=25)
        self.domain = Domain.objects.create(
            domain='supervisr-test.beryju.org')
        self.m_domain = MailDomain.objects.create(
            domain=self.domain)
        self.m_acc_pass = 'b3ryju0rg!'
        self.m_account = MailAccount.objects.create(
            address='smtp-unittest',
            domain=self.m_domain)
        self.m_account.set_password(self.m_acc_pass)

    def tearDown(self):
        self.client.quit()

    def test_connection(self):
        self.client.ehlo()
        self.assertTrue(self.client.does_esmtp)

    def test_login(self):
        self.client.ehlo_or_helo_if_needed()
        self.assertTrue(self.client.login(
            user=self.m_account.email,
            password=self.m_acc_pass))

    def test_send(self):
        self.assertTrue(self.client.login(
            user=self.m_account.email,
            password=self.m_acc_pass))
        # self.assertTrue(self.client.    )
