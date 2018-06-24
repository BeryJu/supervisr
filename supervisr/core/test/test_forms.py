"""Supervisr Core Form Test"""


from supervisr.core.forms.accounts import (ChangePasswordForm, LoginForm,
                                           PasswordResetFinishForm, SignupForm)
from supervisr.core.forms.domains import DomainForm
from supervisr.core.models import Setting, User, UserAcquirableRelationship
from supervisr.core.test.utils import TestCase, internal_provider, test_request
from supervisr.core.views.common import IndexView


class TestForms(TestCase):
    """Supervisr Core Form Test"""

    def setUp(self):
        super(TestForms, self).setUp()
        self.signup_data = {
            'name': 'Test user',
            'username': 'beryjuorg',
            'email': 'test@test.test',
            'password': 'B3ryju0rg!',
            'password_rep': 'B3ryju0rg!',
            'tos_accept': True,
            'g-recaptcha-response': 'PASSED',
            'captcha': 'PASSED',
        }
        self.login_data = {
            'email': 'test@test.test',
            'password': 'B3ryju0rg!',
            'g-recaptcha-response': 'PASSED',
            'captcha': 'PASSED',
        }
        self.change_data = {
            'password': 'B4ryju0rg!',
            'password_rep': 'B4ryju0rg!',
        }

    def test_signup_form(self):
        """Test SignupForm's validation"""
        form = SignupForm(data=self.signup_data)
        self.assertTrue(form.is_valid())

        # Test duplicate username
        user_a = User.objects.create(username='form_test_1')
        self.signup_data['username'] = 'form_test_1'
        form_a = SignupForm(data=self.signup_data)
        self.assertFalse(form_a.is_valid())
        self.signup_data['username'] = 'beryjuorg'
        user_a.delete()

        # Test duplicate email
        self.signup_data['password_rep'] = 'ayy'
        form_b = SignupForm(data=self.signup_data)
        self.assertFalse(form_b.is_valid())
        self.signup_data['password_rep'] = self.signup_data['password']

        # Test wrong password
        user_c = User.objects.create(username='form_test_1', email='dupe@test.test')
        self.signup_data['email'] = 'dupe@test.test'
        form_c = SignupForm(data=self.signup_data)
        self.assertFalse(form_c.is_valid())
        self.signup_data['email'] = 'test@test.test'
        user_c.delete()

        # Test duplicate email (external provider)
        user_d = User.objects.create(username='form_test_1', email='dupee@test.test')
        user_d.email = 'dupe@test.test'
        user_d.save()
        self.signup_data['email'] = 'dupe@test.test'
        form_d = SignupForm(data=self.signup_data)
        self.assertFalse(form_d.is_valid())
        self.signup_data['email'] = 'test@test.test'
        user_d.delete()

    def test_login_form(self):
        """Test LoginForm's validation"""
        form = LoginForm(data=self.login_data)
        self.assertTrue(form.is_valid())

    def test_check_password(self):
        """Test change_password"""
        # Set password filter
        Setting.set(key='password:filter', value=r'(.){8}', namespace='supervisr.core')

        # test one empty password
        form_a = ChangePasswordForm(data={
            'password': 'test',
            'password_rep': '',
        })
        self.assertFalse(form_a.is_valid())

        # test non-matching passwords
        form_b = ChangePasswordForm(data={
            'password': 'test',
            'password_rep': 'testb',
        })
        self.assertFalse(form_b.is_valid())

        # test weak password
        form_c = ChangePasswordForm(data={
            'password': 'test',
            'password_rep': 'test',
        })
        self.assertFalse(form_c.is_valid())

    def test_password_reset_finish_form(self):
        """Test PasswordResetFinishForm"""
        form = PasswordResetFinishForm(data=self.signup_data)
        self.assertTrue(form.is_valid())

    def test_domain_form(self):
        """Test Domain Form"""
        provider, _creds = internal_provider(self.system_user)
        UserAcquirableRelationship.objects.create(
            model=provider,
            user=self.system_user)
        form_request = test_request(IndexView.as_view(), user=self.system_user, just_request=True)

        # Test valid form
        form_a = DomainForm(data={
            'domain_name': 'test.org',
            'provider_instance': provider.pk
        })
        form_a.request = form_request
        self.assertTrue(form_a.is_valid())
        print(form_a.errors)

        # Test invalid domain
        form_b = DomainForm(data={
            'domain_name': 'a-',
            'provider_instance': provider.pk
        })
        form_b.request = form_request
        self.assertFalse(form_b.is_valid())

        # Test invalid provider
        form_c = DomainForm(data={
            'domain_name': 'test.org',
            'provider_instance': -1
        })
        form_c.request = form_request
        self.assertFalse(form_c.is_valid())