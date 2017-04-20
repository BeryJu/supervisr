"""
Supervisr Core Account Test
"""

import os

from django.contrib.auth.models import User
from django.test import TestCase

from ..forms.account import LoginForm, SignupForm
from ..models import AccountConfirmation, get_system_user
from ..signals import SIG_USER_RESEND_CONFIRM
from ..views import account
from .utils import test_request


# pylint: disable=duplicate-code
class TestAccount(TestCase):
    """
    Supervisr Core Account Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.signup_data = {
            'email': 'test@test.test',
            'name': 'Test user',
            'password': 'b3ryju0rg!',
            'password_rep': 'b3ryju0rg!',
            'tos_accept': True,
            'news_accept': False,
            'g-recaptcha-response': 'PASSED',
            'captcha': 'PASSED',
        }
        self.login_data = {
            'email': 'test@test.test',
            'password': 'b3ryju0rg!',
            'g-recaptcha-response': 'PASSED',
            'captcha': 'PASSED',
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
        signup_form = SignupForm(self.signup_data)
        self.assertTrue(signup_form.is_valid())

        res = test_request(account.signup,
                           method='POST',
                           req_kwargs=signup_form.cleaned_data)
        self.assertEqual(res.status_code, 302)

        login_form = LoginForm(self.login_data)
        self.assertTrue(login_form.is_valid())

        res = test_request(account.login,
                           method='POST',
                           req_kwargs=login_form.cleaned_data)
        self.assertEqual(res.status_code, 302)

    def test_signup_view_post(self):
        """
        Test account.signup view POST (Anonymous)
        """
        form = SignupForm(self.signup_data)
        self.assertTrue(form.is_valid())

        res = test_request(account.signup,
                           method='POST',
                           req_kwargs=form.cleaned_data)
        self.assertEqual(res.status_code, 302)

    def test_change_password_init_view(self):
        """
        Test account.reset_password_init view POST (Anonymous)
        """
        form = SignupForm(self.signup_data)
        self.assertTrue(form.is_valid())

        res = test_request(account.signup,
                           method='POST',
                           req_kwargs=form.cleaned_data)
        self.assertEqual(res.status_code, 302)

        res = test_request(account.reset_password_init)
        self.assertEqual(res.status_code, 200)

    def test_resend_confirmation(self):
        """
        Test AccountController.resend_confirmation
        """
        form = SignupForm(self.signup_data)
        self.assertTrue(form.is_valid())

        res = test_request(account.signup,
                           method='POST',
                           req_kwargs=form.cleaned_data)
        self.assertEqual(res.status_code, 302)

        self.assertEqual(len(User.objects.all()), 2)
        user = User.objects.get(email=self.signup_data['email'])
        # Invalidate all other links for this user
        old_acs = AccountConfirmation.objects.filter(
            user=user)
        for old_ac in old_acs:
            old_ac.confirmed = True
            old_ac.save()
        # Create Account Confirmation UUID
        AccountConfirmation.objects.create(user=user)
        SIG_USER_RESEND_CONFIRM.send(
            sender=None,
            user=user,
            req=None)
