"""
Supervisr DNS View Test
"""

# from supervisr.core.models import User
from django.test import RequestFactory, TestCase

# from django.urls import reverse

# from supervisr.core.models import get_system_user
# from supervisr.dns.views import core


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
        pass
        # req = self.factory.get(reverse('dns:index'))
        # req.user = User.objects.get(pk=get_system_user())
        # res = dns.index(req)
        # self.assertEqual(res.status_code, 200)
