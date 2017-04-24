"""
Supervisr Core User Test
"""

import os

from django.contrib.auth.models import User
from django.test import TestCase

from ..forms.account import SignupForm
from ..views import account, user
from .utils import test_request


# pylint: disable=duplicate-code
class TestUser(TestCase):
    """
    Supervisr Core User Test
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

    def test_user_settings(self):
        """
        Test user settings view
        """
        signup_form = SignupForm(self.signup_data)
        self.assertTrue(signup_form.is_valid())

        signup_res = test_request(account.signup,
                                  method='POST',
                                  req_kwargs=signup_form.cleaned_data)
        self.assertEqual(signup_res.status_code, 302)

        m_user = User.objects.get(email=self.signup_data['email'])

        edit_res = test_request(user.index, user=m_user)
        self.assertEqual(edit_res.status_code, 200)


    # def test_user_settings_edit(self):
    #     """
    #     Test user settings view and update a setting
    #     """
    #     signup_form = SignupForm(self.signup_data)
    #     self.assertTrue(signup_form.is_valid())

    #     signup_res = test_request(account.signup,
    #                        method='POST',
    #                        req_kwargs=signup_form.cleaned_data)
    #     self.assertEqual(signup_res.status_code, 302)

    #     m_user = User.objects.get(email=self.signup_data['email'])

    #     edit_res = test_request(user.index,
    #                             user=m_user,
    #                             method='POST',
    #                             req_kwargs={
    #                                 'name':
    #                                 'news_accept': True
    #                             })
    #     self.assertEqual(edit_res.status_code, 200)
    #     print(edit_res.content)
    #     self.assertTrue(m_user.userprofile.news_subscribe, True)

    def test_user_events(self):
        """
        Test user event view
        """
        signup_form = SignupForm(self.signup_data)
        self.assertTrue(signup_form.is_valid())

        signup_res = test_request(account.signup,
                                  method='POST',
                                  req_kwargs=signup_form.cleaned_data)
        self.assertEqual(signup_res.status_code, 302)

        m_user = User.objects.get(email=self.signup_data['email'])

        valid_res = test_request(user.events, user=m_user)
        self.assertEqual(valid_res.status_code, 200)

        invalid_res = test_request(user.events, user=m_user, req_kwargs={'page': 999999})
        self.assertEqual(invalid_res.status_code, 200)