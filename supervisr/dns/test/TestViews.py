"""
Supervisr DNS View Test
"""

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from supervisr.core.models import get_system_user

from ..views import dns


class TestDNSViews(TestCase):
    """
    Supervisr DNS View Test
    """

    def setUp(self):
        self.factory = RequestFactory()

    def test_module_list(self):
        """
        Test module_list view
        """
        req = self.factory.get(reverse('dns:dns-index'))
        req.user = User.objects.get(pk=get_system_user())
        res = dns.index(req)
        self.assertEqual(res.status_code, 200)
