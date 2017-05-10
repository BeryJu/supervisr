"""
Supervisr Mail CommonView Test
"""

import os

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from supervisr.core.models import get_system_user

from ..views import mail


class TestCommonViews(TestCase):
    """
    Supervisr Mail CommonView Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.factory = RequestFactory()

    def test_index_view(self):
        """
        Test Index View (Anonymous)
        """
        req = self.factory.get(reverse('mail:mail-index'))
        req.user = AnonymousUser()
        res = mail.index(req)
        self.assertEqual(res.status_code, 302)

    def test_index_view_auth(self):
        """
        Test Index View (Authenticated)
        """
        req = self.factory.get(reverse('mail:mail-index'))
        req.user = User.objects.get(pk=get_system_user())
        res = mail.index(req)
        self.assertEqual(res.status_code, 200)
