"""Supervisr DNS View Test"""

from supervisr.core.test.utils import TestCase, test_request
from supervisr.dns.views.zones import ZoneIndexView


class TestDNSViews(TestCase):
    """Supervisr DNS View Test"""

    def test_zone_index(self):
        """Test zone_index view"""
        self.assertEqual(test_request(ZoneIndexView.as_view(),
                                      user=self.system_user).status_code, 200)
