"""
Supervisr Core AdminView Test
"""

from django.test import TestCase
from supervisr.core.models import get_system_user
from supervisr.core.tests.utils import test_request
from supervisr.core.views import admin


class TestAdminViews(TestCase):
    """
    Supervisr Core AdminView Test
    """

    def test_info_view(self):
        """
        Test Info View
        """
        self.assertEqual(test_request(admin.info, user=get_system_user()).status_code, 200)
