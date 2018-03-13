"""Supervisr Core CommonView Test"""


import os

from django.test import RequestFactory, TestCase
from django.urls import reverse

from supervisr.core.models import (Setting, SVAnonymousUser, User,
                                   get_system_user)
from supervisr.core.views import common


class TestCommonViews(TestCase):
    """Supervisr Core CommonView Test"""

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        Setting.set('analytics:ga:enabled', True)
        self.factory = RequestFactory()

    def test_index_view(self):
        """Test Index View (Anonymous)"""
        request = self.factory.get(reverse('common-index'))
        request.user = SVAnonymousUser()
        response = common.IndexView.as_view()(request)
        self.assertEqual(response.status_code, 302)

    def test_index_view_auth(self):
        """Test Index View (Authenticated)"""
        request = self.factory.get(reverse('common-index'))
        request.user = User.objects.get(pk=get_system_user())
        response = common.IndexView.as_view()(request)
        self.assertEqual(response.status_code, 200)
