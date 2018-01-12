"""
Supervisr Web View Test
"""

from django.test import RequestFactory, TestCase
from django.urls import reverse

from supervisr.core.models import User, get_system_user
from supervisr.web.views import web


class TestWebViews(TestCase):
    """
    Supervisr Web View Test
    """

    def setUp(self):
        self.factory = RequestFactory()

    def test_module_list(self):
        """
        Test module_list view
        """
        req = self.factory.get(reverse('supervisr_web:index'))
        req.user = User.objects.get(pk=get_system_user())
        res = web.index(req)
        self.assertEqual(res.status_code, 200)
