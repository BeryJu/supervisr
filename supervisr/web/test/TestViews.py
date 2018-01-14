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
        request = self.factory.get(reverse('supervisr_web:index'))
        request.user = User.objects.get(pk=get_system_user())
        response = web.index(request)
        self.assertEqual(response.status_code, 200)
