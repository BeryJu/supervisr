"""
Supervisr Static View Test
"""

from django.test import TestCase

from supervisr.core.models import User, get_system_user
from supervisr.core.test.utils import test_request
from supervisr.static import views


class TestViews(TestCase):
    """
    Supervisr Static View Test
    """

    def setUp(self):
        self.user = User.objects.get(pk=get_system_user())

    def test_single_view(self):
        """
        Test Single View
        """
        self.assertEqual(test_request(views.view, url_kwargs={
            'slug': 'changelog',
            }).status_code, 200)

    def test_single_view_auth(self):
        """
        Test Single View (authenticated)
        """
        self.assertEqual(test_request(views.view, user=self.user, url_kwargs={
            'slug': 'changelog',
            }).status_code, 200)

    def test_single_view_not_found(self):
        """
        Test Single View (invalid slug)
        """
        self.assertEqual(test_request(views.view, url_kwargs={
            'slug': 'qqqqqqqqqqqqqqqqq',
            }).status_code, 404)

    def test_feed_view(self):
        """
        Test Feed View
        """
        self.assertEqual(test_request(views.feed).status_code, 200)

    def test_feed_view_auth(self):
        """
        Test Feed View (authenticated)
        """
        self.assertEqual(test_request(views.feed, user=self.user).status_code, 200)

    def test_feed_view_invalid_page(self):
        """
        Test Feed View (invalid page)
        """
        self.assertEqual(test_request(views.feed, req_kwargs={
            'page': 999999999
            }).status_code, 200)
