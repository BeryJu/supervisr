"""
Supervisr Core DomainView Test
"""


import os

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.urls import reverse

from supervisr.core.models import User, get_system_user
from supervisr.core.views import domains


class TestDomainViews(TestCase):
    """
    Supervisr Core DomainView Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.factory = RequestFactory()

    def test_index_view(self):
        """
        Test Index View (Anonymous)
        """
        req = self.factory.get(reverse('domain-index'))
        req.user = AnonymousUser()
        res = domains.index(req)
        self.assertEqual(res.status_code, 302)

    def test_index_view_auth(self):
        """
        Test Index View (Authenticated)
        """
        req = self.factory.get(reverse('domain-index'))
        req.user = User.objects.get(pk=get_system_user())
        res = domains.index(req)
        self.assertEqual(res.status_code, 200)
