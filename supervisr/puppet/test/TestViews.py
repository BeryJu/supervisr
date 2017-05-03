"""
Supervisr Puppet View Test
"""

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.urls import reverse

from supervisr.puppet import views


# pylint: disable=duplicate-code
class TestPuppetViews(TestCase):
    """
    Supervisr Puppet View Test
    """

    def setUp(self):
        self.factory = RequestFactory()

    def test_module_list(self):
        """
        Test module_list view
        """
        req = self.factory.get(reverse('puppet:module-list'))
        req.user = AnonymousUser()
        res = views.module_list(req)
        self.assertEqual(res.status_code, 501)

    def test_module(self):
        """
        Test module view
        """
        kwargs = {'user': 'testuser', 'module': 'testmodule'}
        req = self.factory.get(reverse('puppet:module', kwargs=kwargs))
        req.user = AnonymousUser()
        res = views.module(req, **kwargs)
        self.assertEqual(res.status_code, 501)

    def test_user_list(self):
        """
        Test user_list view
        """
        req = self.factory.get(reverse('puppet:user-list'))
        req.user = AnonymousUser()
        res = views.user_list(req)
        self.assertEqual(res.status_code, 501)

    def test_user(self):
        """
        Test user view
        """
        kwargs = {'user': 'testuser'}
        req = self.factory.get(reverse('puppet:user', kwargs=kwargs))
        req.user = AnonymousUser()
        res = views.user(req, **kwargs)
        self.assertEqual(res.status_code, 501)

    def test_release(self):
        """
        Test release view
        """
        kwargs = {'user': 'testuser', 'module': 'testmodule', 'version': '0.1.1'}
        req = self.factory.get(reverse('puppet:release', kwargs=kwargs))
        req.user = AnonymousUser()
        res = views.release(req, **kwargs)
        self.assertEqual(res.status_code, 501)
