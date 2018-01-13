"""
Supervisr Server View Test
"""

from django.test import RequestFactory, TestCase
from django.urls import reverse

from supervisr.core.models import User, get_system_user
from supervisr.server.views import server


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
        request = self.factory.get(reverse('supervisr_server:index'))
        request.user = User.objects.get(pk=get_system_user())
        response = server.index(request)
        self.assertEqual(response.status_code, 200)
