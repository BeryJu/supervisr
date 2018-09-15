"""Supervisr Core API Test"""
from unittest.mock import patch

from django.core.exceptions import PermissionDenied
from django.http import Http404

from supervisr.core.api.base import API
from supervisr.core.exceptions import UnauthorizedException
from supervisr.core.utils.tests import TestCase, test_request


class TestBaseAPI(TestCase):
    """Supervisr Core API Test"""

    def setUp(self):
        super().setUp()
        self.api_instance = API()
        self.api_instance.ALLOWED_VERBS['GET'] += ['test']
        self.request = test_request(API.as_view(), user=self.system_user, just_request=True)

    @patch('supervisr.core.api.base.API.pre_handler')
    def test_api_unauthorized(self, pre_handler):
        """Test Base API unauthorized"""
        pre_handler.side_effect = UnauthorizedException
        self.assertIn('unauthorized', self.api_instance.dispatch(
            self.request, verb='test').content.decode('utf-8'))

    @patch('supervisr.core.api.base.API.pre_handler')
    def test_api_permission_denied(self, pre_handler):
        """Test Base API permission denied"""
        pre_handler.side_effect = PermissionDenied
        self.assertIn('permission denied', self.api_instance.dispatch(
            self.request, verb='test').content.decode('utf-8'))

    @patch('supervisr.core.api.base.API.pre_handler')
    def test_api_key_error(self, pre_handler):
        """Test Base API key error"""
        pre_handler.side_effect = KeyError('test')
        self.assertIn('test', self.api_instance.dispatch(
            self.request, verb='test').content.decode('utf-8'))

    @patch('supervisr.core.api.base.API.pre_handler')
    def test_api_404(self, pre_handler):
        """Test Base API 404"""
        pre_handler.side_effect = Http404
        self.assertIn('not found', self.api_instance.dispatch(
            self.request, verb='test').content.decode('utf-8'))
