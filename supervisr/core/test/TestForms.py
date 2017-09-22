"""
Supervisr Core Form Test
"""

import os

from django.contrib.auth.models import User
from django.test import TestCase

from supervisr.core.forms.accounts import (ChangePasswordForm, LoginForm,
                                           PasswordResetFinishForm, SignupForm)
from supervisr.core.forms.domains import DomainForm
from supervisr.core.models import (ProviderInstance, Setting,
                                   UserProductRelationship, UserProfile,
                                   get_system_user)
from supervisr.core.providers.internal import InternalCredential
from supervisr.core.test.utils import test_request
from supervisr.core.views.common import index


class TestForms(TestCase):
    """
    Supervisr Core Form Test
    """

    # pylint: disable=duplicate-code
    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
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
        """
        Test SignupForm's validation
        """
        form = SignupForm(data=self.signup_data)
        self.assertTrue(form.is_valid())

        # Test duplicate username
        user_b = User.objects.create(username='form_test_1')
        prof_b = UserProfile.objects.create(username='form_test_1', user=user_b)
        self.signup_data['username'] = 'form_test_1'
        form_b = SignupForm(data=self.signup_data)
        self.assertFalse(form_b.is_valid())
        self.signup_data['username'] = 'beryjuorg'
        user_b.delete()
        prof_b.delete()

        # Test duplicate email
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
        """
        Test LoginForm's validation
        """
        form = LoginForm(data=self.login_data)
        self.assertTrue(form.is_valid())

    def test_check_password(self):
        """
        Test change_password
        """
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
        """
        Test PasswordResetFinishForm
        """
        form = PasswordResetFinishForm(data=self.signup_data)
        self.assertTrue(form.is_valid())

    def test_domain_form(self):
        """
        Test Domain Form
        """
        user = User.objects.get(pk=get_system_user())
        creds = InternalCredential.objects.create(
            owner=user,
            name='internal')
        prov_inst = ProviderInstance.objects.create(
            credentials=creds,
            provider_path='supervisr.core.providers.internal.InternalBaseProvider')
        UserProductRelationship.objects.create(
            product=prov_inst,
            user=user)

        # Test valid form
        form_a = DomainForm(data={
            'domain': 'test.org',
            'provider': prov_inst.pk
        })
        form_a.request = test_request(index, user=user, just_request=True)
        self.assertTrue(form_a.is_valid())

        # Test invalid domain
        form_b = DomainForm(data={
            'domain': '1test.',
            'provider': prov_inst.pk
        })
        form_b.request = test_request(index, user=user, just_request=True)
        self.assertFalse(form_b.is_valid())

        # Test invalid provider
        form_c = DomainForm(data={
            'domain': 'test.org',
            'provider': -1
        })
        form_c.request = test_request(index, user=user, just_request=True)
        self.assertFalse(form_c.is_valid())
