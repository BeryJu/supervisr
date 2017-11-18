"""
Supervisr Core Account Test
"""

import os

from django.contrib.auth.models import User
from django.test import TestCase

from ..ldap_connector import LDAPConnector


class TestAccountLDAP(TestCase):
    """
    Supervisr Core Account Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.ldap = LDAPConnector(mock=True)
        self.password = 'b3ryju0rg!'
        self.user = User.objects.create_user(
            username='test@test.test',
            email='test@test.test',
            first_name='Test user')
        self.user.save()
        self.user.is_active = False
        self.user.set_password(self.password)
        self.user.save()

    def test_new_user(self):
        """
        Test new new ldap user
        """
        self.assertTrue(self.ldap.create_ldap_user(self.user, self.password))

    def test_change_password(self):
        """
        Test ldap change_password
        """
        self.assertTrue(self.ldap.create_ldap_user(self.user, self.password))
        self.assertTrue(self.ldap.change_password('b4ryju1rg!', mail=self.user.email))
        self.assertTrue(self.ldap.change_password('b3ryju0rg!', mail=self.user.email))

    def test_disable_enable(self):
        """
        Test ldap enable and disable
        """
        self.assertTrue(self.ldap.create_ldap_user(self.user, self.password))
        self.assertTrue(self.ldap.disable_user(mail=self.user.email))
        self.assertTrue(self.ldap.enable_user(mail=self.user.email))

    def test_email_used(self):
        """
        Test ldap is_email_used
        """
        self.assertTrue(self.ldap.create_ldap_user(self.user, self.password))
        self.assertTrue(self.ldap.is_email_used(self.user.email))

    def test_auth(self):
        """
        Test ldap auth
        """
        self.assertTrue(self.ldap.create_ldap_user(self.user, self.password))
        # self.assertTrue(self.ldap.auth_user(self.password, mail=self.user.email))
