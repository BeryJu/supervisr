"""
Supervisr Core API Test
"""

from django.contrib.auth.models import User
from django.test import TestCase

from supervisr.core.api.v1 import user as v1_user
from supervisr.core.models import get_system_user
from supervisr.core.test.utils import oauth2_get_token, test_request


class TestAPIs(TestCase):
    """
    Supervisr Core API Test
    """

    def setUp(self):
        """
        Create user and token to use
        """
        self.user = User.objects.get(pk=get_system_user())
        self.token = oauth2_get_token(self.user)

    def test_json(self):
        """
        Test json request
        """
        self.assertEqual(
            test_request(
                v1_user.account_me,
                user=self.user,
                req_kwargs={'format': 'json'},
                headers={'HTTP_AUTHORIZATION': self.token}
                ).status_code, 200)

    def test_openid(self):
        """
        Test openid request
        """
        self.assertEqual(
            test_request(
                v1_user.account_me,
                user=self.user,
                req_kwargs={'format': 'openid'},
                headers={'HTTP_AUTHORIZATION': self.token}
                ).status_code, 200)

    def test_yaml(self):
        """
        Test yaml request
        """
        self.assertEqual(
            test_request(
                v1_user.account_me,
                user=self.user,
                req_kwargs={'format': 'yaml'},
                headers={'HTTP_AUTHORIZATION': self.token}
                ).status_code, 200)

    def test_invalid(self):
        """
        Test invalid request
        """
        self.assertEqual(
            test_request(
                v1_user.account_me,
                user=self.user,
                req_kwargs={'format': 'invalid'},
                headers={'HTTP_AUTHORIZATION': self.token}
                ).status_code, 200)
