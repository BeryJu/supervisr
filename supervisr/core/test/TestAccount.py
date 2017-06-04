"""
Supervisr Core Account Test
"""

import os

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from ..forms.account import ChangePasswordForm, LoginForm, SignupForm
from ..models import AccountConfirmation, get_system_user
from ..signals import SIG_USER_RESEND_CONFIRM
from ..views import account, common
from .utils import test_request


class TestAccount(TestCase):
    """
    Supervisr Core Account Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.signup_data = {
            'email': 'test@test.test',
            'username': 'beryjuorg',
            'name': 'Test user',
            'password': 'b3ryju0rg!',
            'password_rep': 'b3ryju0rg!',
            'tos_accept': True,
            'g-recaptcha-response': 'PASSED',
            'captcha': 'PASSED',
        }
        self.login_data = {
            'email': 'test@test.test',
            'password': 'b3ryju0rg!',
            'g-recaptcha-response': 'PASSED',
            'captcha': 'PASSED',
        }
        self.change_data = {
            'password': 'b4ryju0rg!',
            'password_rep': 'b4ryju0rg!',
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
        # test login with post
        form = LoginForm(self.login_data)
        self.assertTrue(form.is_valid())

        res = test_request(account.login,
                           method='POST',
                           req_kwargs=form.cleaned_data)
        self.assertEqual(res.status_code, 302)

    def test_logout_view(self):
        """
        Test account.logout view
        """
        res = test_request(account.logout,
                           user=get_system_user())
        self.assertEqual(res.status_code, 302)

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

        signup_res = test_request(account.signup,
                                  method='POST',
                                  req_kwargs=signup_form.cleaned_data)
        self.assertEqual(signup_res.status_code, 302)

        # Manually activate the account so we can log in
        user = User.objects.filter(email=self.signup_data['email']).first()
        user.is_active = True
        user.save()

        login_res = test_request(account.login,
                                 method='POST',
                                 req_kwargs=self.login_data)
        self.assertEqual(login_res.status_code, 302)
        self.assertEqual(login_res.url, reverse(common.index))

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
        new_ac = AccountConfirmation.objects.create(user=user)
        self.assertFalse(new_ac.is_expired)
        SIG_USER_RESEND_CONFIRM.send(
            sender=None,
            user=user,
            req=None)

    def test_change_password(self):
        """
        Test account.change_password view POST
        """
        signup_form = SignupForm(self.signup_data)
        self.assertTrue(signup_form.is_valid())

        signup_res = test_request(account.signup,
                                  method='POST',
                                  req_kwargs=signup_form.cleaned_data)
        self.assertEqual(signup_res.status_code, 302)

        # Manually activate the account so we can log in
        user = User.objects.filter(email=self.signup_data['email']).first()
        # activate_res = test_request(account.confirm,
        #                             url_kwargs={
        #                                 'uuid': AccountConfirmation.objects.
        #                                         filter(user=user).first().pk
        #                             })
        # self.assertEqual(activate_res.status_code, 302)
        # self.assertEqual(activate_res.url, reverse(account.login))

        # Test form rendering
        self.assertEqual(test_request(account.change_password, user=user).status_code, 200)

        # Test actual password changing
        change_form = ChangePasswordForm(self.change_data)
        self.assertTrue(change_form.is_valid())

    #     change_res = test_request(account.change_password,
    #                               method='POST',
    #                               user=user,
    #                               req_kwargs=self.change_data)

    #     self.assertEqual(change_res.status_code, 302)
    #     self.assertEqual(change_res.url, reverse(common.index))
