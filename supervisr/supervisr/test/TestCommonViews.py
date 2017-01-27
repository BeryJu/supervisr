"""
Supervisr Core CommonView Test
"""

# pylint: disable=duplicate-code
import os

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from ..models import Setting, get_system_user
from ..views import common


# pylint: disable=duplicate-code
class TestCommonViews(TestCase):
    """
    Supervisr Core CommonView Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        Setting.set('supervisr:analytics:ga:enabled', True)
        self.factory = RequestFactory()

    def test_index_view(self):
        """
        Test Index View (Anonymous)
        """
        req = self.factory.get(reverse('common-index'))
        req.user = AnonymousUser()
        res = common.index(req)
        self.assertEqual(res.status_code, 302)

    def test_index_view_auth(self):
        """
        Test Index View (Authenticated)
        """
        req = self.factory.get(reverse('common-index'))
        req.user = User.objects.get(pk=get_system_user())
        res = common.index(req)
        self.assertEqual(res.status_code, 200)
