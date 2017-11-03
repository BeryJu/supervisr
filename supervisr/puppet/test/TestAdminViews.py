"""
Supervisr Puppet View Test
"""

from django.test import TestCase

from supervisr.core.models import get_system_user
from supervisr.core.test.utils import test_request
from supervisr.puppet.views import admin


class TestAdminViews(TestCase):
    """Supervisr Puppet View Test"""

    def test_index(self):
        """Test index view"""
        self.assertEqual(test_request(admin.index, user=get_system_user()).status_code, 200)

    def test_debug_build_valid(self):
        """Test debug_build view (valid data)"""
        self.assertEqual(test_request(admin.debug_build,
                                      user=get_system_user(),
                                      url_kwargs={
                                          'user': 'supervisr',
                                          'module': 'supervisr_core'
                                      }).status_code, 302)

    def test_debug_build_invalid(self):
        """Test debug_build view (invalid data)"""
        self.assertEqual(test_request(admin.debug_build,
                                      user=get_system_user(),
                                      url_kwargs={
                                          'user': 'qwerqwer',
                                          'module': 'supervisr_core'
                                      }).status_code, 404)
        self.assertEqual(test_request(admin.debug_build,
                                      user=get_system_user(),
                                      url_kwargs={
                                          'user': 'supervisr',
                                          'module': 'superqwerqwrvisr_core'
                                      }).status_code, 404)

    def test_debug_render(self):
        """Test debug_render view (GET)"""
        self.assertEqual(test_request(admin.debug_render,
                                      user=get_system_user()).status_code, 200)

    def test_debug_render_post(self):
        """Test debug_render view (POST)"""
        self.assertEqual(test_request(admin.debug_render,
                                      method='POST',
                                      user=get_system_user(),
                                      req_kwargs={
                                          'templatepath': 'supervisr/core/server/'
                                                          'config/manifests/users/normal.pp'
                                      }).status_code, 200)

    def test_debug_render_invalid(self):
        """Test debug_render view (POST, invalid path)"""
        self.assertEqual(test_request(admin.debug_render,
                                      method='POST',
                                      user=get_system_user(),
                                      req_kwargs={
                                          'templatepath': 'aaaa'
                                      }).status_code, 200)