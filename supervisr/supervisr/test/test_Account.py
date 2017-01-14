import os
from unittest import skip

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase

from ..controllers import AccountController
from ..forms.account import *
from ..ldap_connector import LDAPConnector
from ..models import *
from ..views import account
from .utils import test_request


class AccountTestCase(TestCase):

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.factory = RequestFactory()
        self.ldap = LDAPConnector(mock=True)
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
        form = SignupForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_signup(self):
        self.assertTrue(AccountController.signup(
            name=self.data['name'],
            email=self.data['email'],
            password=self.data['password'],
            ldap=self.ldap))

    def test_signup_change_password(self):
        self.assertTrue(AccountController.signup(
            name=self.data['name'],
            email=self.data['email'],
            password=self.data['password'],
            ldap=self.ldap))
        self.assertTrue(AccountController.change_password(
            email=self.data['email'],
            password='b4ryju1rg',
            ldap=self.ldap))

    def test_ldap(self):
        self.assertTrue(LDAPConnector.enabled())

    def test_signup_view(self):
        res = test_request(account.signup)
        self.assertEqual(res.status_code, 200)

    def test_login_view(self):
        res = test_request(account.login)
        self.assertEqual(res.status_code, 200)

    def test_signup_view_auth(self):
        res = test_request(account.signup,
            user=get_system_user())
        self.assertEqual(res.status_code, 302)

    def test_login_view_auth(self):
        res = test_request(account.login,
            user=get_system_user())
        self.assertEqual(res.status_code, 302)

    def test_login_view_post(self):
        self.test_signup_view_post()
        self.assertTrue(AccountController.signup(
            name=self.data['name'],
            email=self.data['email'],
            password=self.data['password'],
            ldap=self.ldap))
        form = LoginForm(self.data)
        self.assertTrue(form.is_valid())

        res = test_request(account.login,
            method='POST',
            req_kwargs=form.cleaned_data)
        self.assertEqual(res.status_code, 200)

    def test_signup_view_post(self):
        form = SignupForm(self.data)
        self.assertTrue(form.is_valid())

        res = test_request(account.signup,
            method='POST',
            req_kwargs=form.cleaned_data)
        self.assertEqual(res.status_code, 200)

    def test_change_password_init_view(self):
        self.assertTrue(AccountController.signup(
            name=self.data['name'],
            email=self.data['email'],
            password=self.data['password'],
            ldap=self.ldap))

        user = User.objects.get(email=self.data['email'])
        res = test_request(account.reset_password_init)
        self.assertEqual(res.status_code, 200)
