import os
from unittest import skip

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from ..controllers import AccountController
from ..forms.account import *
from ..ldap_connector import LDAPConnector
from ..models import *


class AccountTestCase(TestCase):

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.factory = RequestFactory()
        self.ldap = LDAPConnector(mock=True)
        self.form = SignupForm()
        self.data = {
            'email': 'test@test.test',
            'name': 'Test user',
            'password': 'b3ryju0rg!',
            'password_rep': 'b3ryju0rg!',
            'tos_accept': True,
            'news_accept': False,
            'g-recaptcha-response': "PASSED"
        }

    def test_signup_form(self):
        self.form = SignupForm(data=self.data)
        self.assertTrue(self.form.is_valid())

    def test_signup(self):
        self.assertTrue(AccountController.signup(
            name=self.data['name'],
            email=self.data['email'],
            password=self.data['password']))

    def test_change_password(self):
        self.assertTrue(AccountController.signup(
            name=self.data['name'],
            email=self.data['email'],
            password=self.data['password']))
        self.assertTrue(AccountController.change_password(
            email=self.data['email'],
            password='b4ryju1rg'))

    @skip("TODO: finish LDAP Mocking for unittests")
    def test_ldap(self):
        self.assertTrue(LDAPConnector.enabled())
