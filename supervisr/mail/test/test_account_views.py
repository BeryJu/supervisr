"""
Supervisr Mail AccountView Test
"""

import os

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.urls import reverse

from supervisr.core.models import User, get_system_user
from supervisr.mail.views import account


class TestAccountViews(TestCase):
    """
    Supervisr Mail AccountView Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.factory = RequestFactory()

    def test_index_view(self):
        """
        Test Index View (Anonymous)
        """
        request = self.factory.get(reverse('supervisr_mail:mail-account-index'))
        request.user = AnonymousUser()
        response = account.index(request)
        self.assertEqual(response.status_code, 302)

    def test_index_view_auth(self):
        """
        Test Index View (Authenticated)
        """
        request = self.factory.get(reverse('supervisr_mail:mail-account-index'))
        request.user = User.objects.get(pk=get_system_user())
        response = account.index(request)
        self.assertEqual(response.status_code, 200)
