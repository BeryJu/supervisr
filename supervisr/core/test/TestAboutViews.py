"""
Supervisr Core AboutView Test
"""

from django.test import TestCase

from ..views import about
from .utils import test_request


class TestAboutViews(TestCase):
    """
    Supervisr Core AboutView Test
    """

    def test_changelog_view(self):
        """
        Test Changelog View
        """
        self.assertEqual(test_request(about.changelog).status_code, 200)

    def test_attributions_view(self):
        """
        Test attributions view
        """
        self.assertEqual(test_request(about.attributions).status_code, 200)
