"""Supervisr Core API Test"""

from supervisr.core.api.v1.accounts import AccountAPI
from supervisr.core.api.v1.credentials import CredentialAPI
from supervisr.core.utils.tests import TestCase, test_request


class TestAPIs(TestCase):
    """Supervisr Core API Test"""

    def test_credentials(self):
        """Test Credentials API"""
        CredentialAPI()

    def test_json(self):
        """Test json request"""
        self.assertEqual(
            test_request(
                AccountAPI.as_view(),
                user=self.system_user,
                url_kwargs={'verb': 'me'},
                req_kwargs={'format': 'json'},
            ).status_code, 200)

    def test_openid(self):
        """Test openid request"""
        self.assertEqual(
            test_request(
                AccountAPI.as_view(),
                user=self.system_user,
                url_kwargs={'verb': 'me'},
                req_kwargs={'format': 'openid'},
            ).status_code, 200)

    def test_yaml(self):
        """Test yaml request"""
        self.assertEqual(
            test_request(
                AccountAPI.as_view(),
                user=self.system_user,
                url_kwargs={'verb': 'me'},
                req_kwargs={'format': 'yaml'},
            ).status_code, 200)

    def test_invalid(self):
        """Test invalid request"""
        self.assertEqual(
            test_request(
                AccountAPI.as_view(),
                user=self.system_user,
                url_kwargs={'verb': 'me'},
                req_kwargs={'format': 'invalid'},
            ).status_code, 400)
        self.assertEqual(
            test_request(
                AccountAPI.as_view(),
                user=self.system_user,
                url_kwargs={'verb': 'invalid'},
                req_kwargs={'format': 'invalid'},
            ).status_code, 400)
