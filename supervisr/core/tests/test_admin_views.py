"""Supervisr Core AdminView Test"""

from supervisr.core.tests.utils import TestCase, test_request
from supervisr.core.views import admin


class TestAdminViews(TestCase):
    """Supervisr Core AdminView Test"""

    def test_index_view(self):
        """Test index View"""
        self.assertEqual(test_request(admin.IndexView.as_view(),
                                      user=self.system_user).status_code, 200)

    def test_user_view(self):
        """Test user View"""
        self.assertEqual(test_request(admin.UserIndexView.as_view(),
                                      user=self.system_user).status_code, 200)

    def test_event_view(self):
        """Test event View"""
        self.assertEqual(test_request(admin.EventView.as_view(),
                                      user=self.system_user).status_code, 200)

    def test_info_view(self):
        """Test Info View"""
        self.assertEqual(test_request(admin.InfoView.as_view(),
                                      user=self.system_user).status_code, 200)
