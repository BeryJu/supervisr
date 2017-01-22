"""
Supervisr Core AboutView Test
"""

import os

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from ..models import get_system_user
from ..views import about


# pylint: disable=duplicate-code
class TestAboutViews(TestCase):
    """
    Supervisr Core AboutView Test
    """

    def setUp(self):
        self.factory = RequestFactory()

    def test_info_view(self):
        """
        Test Info View
        """
        req = self.factory.get(reverse('about-info'))
        req.user = User.objects.get(pk=get_system_user())
        res = about.info(req)
        self.assertEqual(res.status_code, 200)

    def test_changelog_view(self):
        """
        Test Changelog View
        """
        req = self.factory.get(reverse('about-changelog'))
        req.user = AnonymousUser()
        res = about.changelog(req)
        self.assertEqual(res.status_code, 200)
