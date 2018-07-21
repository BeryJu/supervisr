"""Supervisr Core DomainView Test"""


from django.test import TestCase

from supervisr.core.models import get_system_user
from supervisr.core.tests.utils import test_request
from supervisr.core.views import domains


class TestDomainViews(TestCase):
    """Supervisr Core DomainView Test"""

    def test_index_view(self):
        """Test Index View (Anonymous)"""
        self.assertEqual(test_request(domains.DomainIndexView.as_view()).status_code, 302)

    def test_index_view_auth(self):
        """Test Index View (Authenticated)"""
        self.assertEqual(test_request(
            domains.DomainIndexView.as_view(), user=get_system_user()).status_code, 200)
