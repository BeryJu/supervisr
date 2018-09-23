"""Supervisr Core Account Test"""

from django.http import HttpRequest
from django.urls import reverse

from supervisr.core.decorators import reauth_required
from supervisr.core.forms.accounts import (ChangePasswordForm, LoginForm,
                                           SignupForm)
from supervisr.core.models import AccountConfirmation, User
from supervisr.core.signals import on_user_confirm_resend
from supervisr.core.utils.tests import TestCase, test_request
from supervisr.core.views import accounts


class TestAccount(TestCase):
    """Supervisr Core Account Test"""

    def setUp(self):
        super(TestAccount, self).setUp()
        self.signup_data = {
            'name': 'Test user',
            'username': 'beryjuorg',
            'email': 'unittest@supervisr.beryju.org',
            'password': 'B3ryju0rg!',
            'password_rep': 'B3ryju0rg!',
            'tos_accept': True,
            'g-recaptcha-response': 'PASSED',
            'captcha': 'PASSED',
        }
        self.login_data = {
            'email': 'unittest@supervisr.beryju.org',
            'password': 'B3ryju0rg!',
            'g-recaptcha-response': 'PASSED',
            'captcha': 'PASSED',
        }
        self.change_data = {
            'password_old': 'B3ryju0rg!',
            'password': 'B4ryju0rg!',
            'password_rep': 'B4ryju0rg!',
        }

    def test_signup_view(self):
        """Test account.signup view (Anonymous)"""
        res = test_request(accounts.SignUpView.as_view())
        self.assertEqual(res.status_code, 200)

    def test_login_view(self):
        """Test account.login view (Anonymous)"""
        res = test_request(accounts.LoginView.as_view())
        self.assertEqual(res.status_code, 200)
        # test login with post
        form = LoginForm(self.login_data)
        self.assertTrue(form.is_valid())

        res = test_request(accounts.LoginView.as_view(),
                           method='POST',
                           req_kwargs=form.cleaned_data)
        self.assertEqual(res.status_code, 302)

    def test_logout_view(self):
        """Test account.logout view"""
        res = test_request(accounts.LogoutView.as_view(), user=self.system_user)
        self.assertEqual(res.status_code, 302)

    def test_signup_view_auth(self):
        """Test account.signup view (Authenticated)"""
        res = test_request(accounts.SignUpView.as_view(), user=self.system_user)
        self.assertEqual(res.status_code, 302)

    def test_login_view_auth(self):
        """Test account.login view (Authenticated)"""
        res = test_request(accounts.LoginView.as_view(), user=self.system_user)
        self.assertEqual(res.status_code, 302)

    def test_login_view_post(self):
        """Test account.login view POST (Anonymous)"""
        signup_form = SignupForm(self.signup_data)
        self.assertTrue(signup_form.is_valid())

        signup_res = test_request(accounts.SignUpView.as_view(),
                                  method='POST',
                                  req_kwargs=signup_form.cleaned_data)
        self.assertEqual(signup_res.status_code, 302)

        # Manually activate the account so we can log in
        user = User.objects.filter(email=self.signup_data['email']).first()
        user.is_active = True
        user.save()

        login_res = test_request(accounts.LoginView.as_view(),
                                 method='POST',
                                 req_kwargs=self.login_data)
        self.assertEqual(login_res.status_code, 302)
        self.assertEqual(login_res.url, reverse('common-index'))

    def test_signup_view_post(self):
        """Test account.signup view POST (Anonymous)"""
        form = SignupForm(self.signup_data)
        self.assertTrue(form.is_valid())

        res = test_request(accounts.SignUpView.as_view(),
                           method='POST',
                           req_kwargs=form.cleaned_data)
        self.assertEqual(res.status_code, 302)

    def test_change_password(self):
        """Test account.change_password"""
        signup_form = SignupForm(self.signup_data)
        self.assertTrue(signup_form.is_valid())

        signup_res = test_request(accounts.SignUpView.as_view(),
                                  method='POST',
                                  req_kwargs=signup_form.cleaned_data)
        self.assertEqual(signup_res.status_code, 302)

        # Manually activate the account so we can log in
        user = User.objects.filter(email=self.signup_data['email']).first()
        user.is_active = True
        user.save()

        # ChangePasswordForm requires a request to verify the current password
        form_request = test_request(accounts.ChangePasswordView.as_view(),
                                    user=user, just_request=True)
        form = ChangePasswordForm(self.change_data)
        form.request = form_request
        self.assertTrue(form.is_valid())

        res = test_request(accounts.ChangePasswordView.as_view(),
                           user=user,
                           method='POST',
                           req_kwargs=form.cleaned_data)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse('common-index'))

        res = test_request(accounts.ChangePasswordView.as_view(), user=user)
        self.assertEqual(res.status_code, 200)

    def test_reset_password_init_view(self):
        """
        Test account.reset_password_init view POST (Anonymous)
        """
        form = SignupForm(self.signup_data)
        self.assertTrue(form.is_valid())

        res = test_request(accounts.SignUpView.as_view(),
                           method='POST',
                           req_kwargs=form.cleaned_data)
        self.assertEqual(res.status_code, 302)

        res = test_request(accounts.PasswordResetInitView.as_view())
        self.assertEqual(res.status_code, 200)

    def test_resend_confirmation(self):
        """
        Test AccountController.resend_confirmation
        """
        form = SignupForm(self.signup_data)
        self.assertTrue(form.is_valid())

        res = test_request(accounts.SignUpView.as_view(),
                           method='POST',
                           req_kwargs=form.cleaned_data)
        self.assertEqual(res.status_code, 302)
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
        on_user_confirm_resend.send(
            sender=None,
            user=user,
            request=None)

    def test_reset_passowrd(self):
        """
        Test reset password POST
        """
        # Signup user first
        signup_form = SignupForm(self.signup_data)
        self.assertTrue(signup_form.is_valid())

        signup_res = test_request(accounts.SignUpView.as_view(),
                                  method='POST',
                                  req_kwargs=signup_form.cleaned_data)
        self.assertEqual(signup_res.status_code, 302)

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
        uuid = AccountConfirmation.objects.filter(user=user).first().pk
        reset_res = test_request(accounts.PasswordResetFinishView.as_view(),
                                 method='POST',
                                 user=user,
                                 url_kwargs={'uuid': uuid},
                                 req_kwargs=self.change_data)

        self.assertEqual(reset_res.status_code, 302)
        self.assertEqual(reset_res.url, reverse('common-index'))

    def test_reauth(self):
        """Test reauth_required decorator"""
        @reauth_required
        def test_view(request: HttpRequest):
            """Test view"""
            pass

        self.assertEqual(test_request(test_view, ).status_code, 302)
