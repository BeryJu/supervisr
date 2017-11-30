"""
Supervisr Core API Test
"""

from django.test import TestCase

from supervisr.core.api.v1.accounts import AccountAPI
from supervisr.core.api.v1.credentials import CredentialAPI
from supervisr.core.models import User, get_system_user
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

    def test_credentials(self):
        """Test Credentials API"""
        CredentialAPI()

    def test_json(self):
        """
        Test json request
        """
        self.assertEqual(
            test_request(
                AccountAPI.as_view(),
                user=self.user,
                url_kwargs={'verb': 'me'},
                req_kwargs={'format': 'json'},
                ).status_code, 200)

    def test_openid(self):
        """
        Test openid request
        """
        self.assertEqual(
            test_request(
                AccountAPI.as_view(),
                user=self.user,
                url_kwargs={'verb': 'me'},
                req_kwargs={'format': 'openid'},
                ).status_code, 200)

    def test_yaml(self):
        """
        Test yaml request
        """
        self.assertEqual(
            test_request(
                AccountAPI.as_view(),
                user=self.user,
                url_kwargs={'verb': 'me'},
                req_kwargs={'format': 'yaml'},
                ).status_code, 200)

    def test_invalid(self):
        """
        Test invalid request
        """
        self.assertEqual(
            test_request(
                AccountAPI.as_view(),
                user=self.user,
                url_kwargs={'verb': 'me'},
                req_kwargs={'format': 'invalid'},
                ).status_code, 200)
        self.assertEqual(
            test_request(
                AccountAPI.as_view(),
                user=self.user,
                url_kwargs={'verb': 'invalid'},
                req_kwargs={'format': 'invalid'},
                ).status_code, 400)
