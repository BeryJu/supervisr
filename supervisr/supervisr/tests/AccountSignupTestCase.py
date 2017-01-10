from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from ..models import *
from ..forms import *
from ..views.account import *
from ..ldap_connector import LDAPConnector
import os

class AccountSignupTestCase(TestCase):

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.factory = RequestFactory()
        self.ldap = LDAPConnector(mock=True)
        self.form = SignupForm()

    def test_signup_form(self):
        data = {
            'email': 'test@test.test',
            'name': 'Test user',
            'password': 'b3ryju0rg!',
            'password_rep': 'b3ryju0rg!',
            'tos_accept': True,
            'news_accept': False,
            'g-recaptcha-response': "PASSED"
        }
        self.form = SignupForm(data=data)
        self.assertTrue(self.form.is_valid())

    def test_signup(self):
        # data =
        req = self.factory.post('/accounts/signup/')
