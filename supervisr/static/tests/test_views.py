"""Supervisr Static View Test"""

from supervisr.core.tests.utils import TestCase, test_request
from supervisr.static import views


class TestViews(TestCase):
    """ Supervisr Static View Test """

    def test_single_view(self):
        """Test Single View"""
        self.assertEqual(test_request(views.PageView.as_view(), url_kwargs={
            'slug': 'attributions',
        }).status_code, 200)

    def test_single_view_auth(self):
        """Test Single View (authenticated)"""
        self.assertEqual(test_request(views.PageView.as_view(), user=self.system_user, url_kwargs={
            'slug': 'attributions',
        }).status_code, 200)

    def test_single_view_not_found(self):
        """Test Single View (invalid slug)"""
        self.assertEqual(test_request(views.PageView.as_view(), url_kwargs={
            'slug': 'qqqqqqqqqqqqqqqqq',
        }).status_code, 404)

    def test_feed_view(self):
        """Test Feed View"""
        self.assertEqual(test_request(views.FeedView.as_view()).status_code, 200)

    def test_feed_view_auth(self):
        """Test Feed View (authenticated)"""
        self.assertEqual(test_request(views.FeedView.as_view(),
                                      user=self.system_user).status_code, 200)

    def test_feed_view_invalid_page(self):
        """Test Feed View (invalid page)"""
        self.assertEqual(test_request(views.FeedView.as_view(), req_kwargs={
            'page': 999999999
        }).status_code, 200)
