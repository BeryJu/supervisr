"""Supervisr Static View Test"""

from django.test import TestCase

from supervisr.core.models import User, get_system_user
from supervisr.core.test.utils import test_request
from supervisr.static import views
from supervisr.static.models import FilePage


class TestViews(TestCase):
    """ Supervisr Static View Test """

    def setUp(self):
        self.user = User.objects.get(pk=get_system_user())
        names = ['CHANGELOG.md', 'ATTRIBUTIONS.md']
        for name in names:
            page_name = name.split('.')[0]
            FilePage.objects.create(
                title=page_name.title(),
                slug=page_name.lower(),
                path=name,
                author=self.user,
                published=True)

    def test_single_view(self):
        """Test Single View"""
        self.assertEqual(test_request(views.PageView.as_view(), url_kwargs={
            'slug': 'changelog',
        }).status_code, 200)

    def test_single_view_auth(self):
        """Test Single View (authenticated)"""
        self.assertEqual(test_request(views.PageView.as_view(), user=self.user, url_kwargs={
            'slug': 'changelog',
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
                                      user=self.user).status_code, 200)

    def test_feed_view_invalid_page(self):
        """Test Feed View (invalid page)"""
        self.assertEqual(test_request(views.FeedView.as_view(), req_kwargs={
            'page': 999999999
        }).status_code, 200)
