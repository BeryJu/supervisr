"""
Supervisr Server View Test
"""

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from supervisr.core.models import get_system_user

from ..views import server


class TestServerViews(TestCase):
    """
    Supervisr Server View Test
    """

    def setUp(self):
        self.factory = RequestFactory()

    def test_module_list(self):
        """
        Test module_list view
        """
        req = self.factory.get(reverse('supervisr/server:server-index'))
        req.user = User.objects.get(pk=get_system_user())
        res = server.index(req)
        self.assertEqual(res.status_code, 200)
