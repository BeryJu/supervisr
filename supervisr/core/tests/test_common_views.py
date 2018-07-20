"""Supervisr Core CommonView Test"""


from supervisr.core.models import Setting
from supervisr.core.tests.utils import TestCase, test_request
from supervisr.core.views import common


class TestCommonViews(TestCase):
    """Supervisr Core CommonView Test"""

    def setUp(self):
        super(TestCommonViews, self).setUp()
        Setting.set('analytics:ga:enabled', True)

    def test_index_view(self):
        """Test Index View (Anonymous)"""
        self.assertEqual(test_request(common.IndexView.as_view()).status_code, 302)

    def test_index_view_auth(self):
        """Test Index View (Authenticated)"""
        self.assertEqual(test_request(common.IndexView.as_view(),
                                      user=self.system_user).status_code, 200)
