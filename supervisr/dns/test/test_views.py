"""Supervisr DNS View Test"""
from django.test import TestCase

from supervisr.core.models import get_system_user
from supervisr.core.test.utils import test_request
from supervisr.dns.views.zones import ZoneIndexView


class TestDNSViews(TestCase):
    """Supervisr DNS View Test"""

    def test_zone_index(self):
        """Test zone_index view"""
        self.assertEqual(test_request(ZoneIndexView.as_view(),
                                      user=get_system_user()).status_code, 200)
