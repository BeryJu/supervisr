"""
Supervisr Core AdminView Test
"""

from django.test import TestCase

from ..models import get_system_user
from ..views import admin
from .utils import test_request


# pylint: disable=duplicate-code
class TestAdminViews(TestCase):
    """
    Supervisr Core AdminView Test
    """

    def test_info_view(self):
        """
        Test Info View
        """
        self.assertEqual(test_request(admin.info, user=get_system_user()).status_code, 200)
