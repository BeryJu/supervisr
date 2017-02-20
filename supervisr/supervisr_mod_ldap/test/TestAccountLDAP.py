"""
Supervisr Core Account Test
"""

import os

from django.contrib.auth.models import User
from django.test import TestCase

from supervisr.controllers import AccountController
from supervisr.forms.account import LoginForm, SignupForm
from supervisr.models import get_system_user
from supervisr.utils import test_request
from supervisr.views import account

from ..ldap_connector import LDAPConnector


# pylint: disable=duplicate-code
class TestAccountLDAP(TestCase):
    """
    Supervisr Core Account Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.ldap = LDAPConnector(mock=True)
        self.signup_data = {
            'email': 'test@test.test',
            'name': 'Test user',
            'password': 'b3ryju0rg!',
            'password_rep': 'b3ryju0rg!',
            'tos_accept': True,
            'news_accept': False,
            'g-recaptcha-response': "PASSED"
        }
        self.login_data = {
            'email': 'test@test.test',
            'password': 'b3ryju0rg!',
            'g-recaptcha-response': 'PASSED',
        }

    def test_signup_form(self):
        """
        Test SignupForm's validation
        """
        form = SignupForm(data=self.signup_data)
        self.assertTrue(form.is_valid())

    def test_login_form(self):
        """
        Test LoginForm's validation
        """
        form = LoginForm(data=self.login_data)
        self.assertTrue(form.is_valid())

    def test_signup(self):
        """
        Test AccountController's signup
        """
        self.assertTrue(AccountController.signup(
            name=self.signup_data['name'],
            email=self.signup_data['email'],
            password=self.signup_data['password'],
            ldap=self.ldap))

    def test_signup_change_password(self):
        """
        Test AccountController's change_password
        """
        self.assertTrue(AccountController.signup(
            name=self.signup_data['name'],
            email=self.signup_data['email'],
            password=self.signup_data['password'],
            ldap=self.ldap))
        self.assertTrue(AccountController.change_password(
            email=self.signup_data['email'],
            password='b4ryju1rg',
            ldap=self.ldap))

    def test_signup_view(self):
        """
        Test account.signup view (Anonymous)
        """
        res = test_request(account.signup)
        self.assertEqual(res.status_code, 200)

    def test_login_view(self):
        """
        Test account.login view (Anonymous)
        """
        res = test_request(account.login)
        self.assertEqual(res.status_code, 200)

    def test_signup_view_auth(self):
        """
        Test account.signup view (Authenticated)
        """
        res = test_request(account.signup,
                           user=get_system_user())
        self.assertEqual(res.status_code, 302)

    def test_login_view_auth(self):
        """
        Test account.login view (Authenticated)
        """
        res = test_request(account.login,
                           user=get_system_user())
        self.assertEqual(res.status_code, 302)

    def test_login_view_post(self):
        """
        Test account.login view POST (Anonymous)
        """
        self.test_signup_view_post()
        self.assertTrue(AccountController.signup(
            name=self.signup_data['name'],
            email=self.signup_data['email'],
            password=self.signup_data['password'],
            ldap=self.ldap))
        form = LoginForm(self.login_data)
        self.assertTrue(form.is_valid())

        res = test_request(account.login,
                           method='POST',
                           req_kwargs=form.cleaned_data)
        self.assertEqual(res.status_code, 200)

    def test_signup_view_post(self):
        """
        Test account.signup view POST (Anonymous)
        """
        form = SignupForm(self.signup_data)
        self.assertTrue(form.is_valid())

        res = test_request(account.signup,
                           method='POST',
                           req_kwargs=form.cleaned_data)
        self.assertEqual(res.status_code, 200)

    def test_change_password_init_view(self):
        """
        Test account.reset_password_init view POST (Anonymous)
        """
        self.assertTrue(AccountController.signup(
            name=self.signup_data['name'],
            email=self.signup_data['email'],
            password=self.signup_data['password'],
            ldap=self.ldap))

        # user = User.objects.get(email=self.signup_data['email'])
        res = test_request(account.reset_password_init)
        self.assertEqual(res.status_code, 200)

    def test_resend_confirmation(self):
        """
        Test AccountController.resend_confirmation
        """
        self.assertTrue(AccountController.signup(
            name=self.signup_data['name'],
            email=self.signup_data['email'],
            password=self.signup_data['password'],
            ldap=self.ldap))

        user = User.objects.get(email=self.signup_data['email'])
        self.assertTrue(AccountController.resend_confirmation(user))
