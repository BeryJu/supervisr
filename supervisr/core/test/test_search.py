"""Supervisr Core SearchView Test"""

import os

from django.test import TestCase

from supervisr.core.models import Domain, Setting, User, get_system_user
from supervisr.core.test.utils import internal_provider, test_request
from supervisr.core.views import search


class TestSearchView(TestCase):
    """Supervisr Core SearchView Test"""

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        Setting.set('analytics:ga:enabled', True)
        self.user = User.objects.get(pk=get_system_user())

    def test_search_404(self):
        """Test Search without query"""
        res = test_request(search.search, user=self.user)
        self.assertEqual(res.status_code, 404)

    def test_search_empty(self):
        """Test Search with empty results"""
        res = test_request(search.search, user=self.user, req_kwargs={'q': ''})
        self.assertEqual(res.status_code, 200)

    def test_search_domain(self):
        """Test search with 2 domains as result"""
        prov, _creds = internal_provider(self.user)
        Domain.objects.create(provider_instance=prov, domain_name='dom1.supervisr.beryju.org')
        Domain.objects.create(provider_instance=prov, domain_name='dom2.supervisr.beryju.org')
        res = test_request(search.search, user=self.user, req_kwargs={'q': 'supervisr.beryju.org'})
        self.assertEqual(res.status_code, 200)
        self.assertIn('dom1.supervisr.beryju.org', str(res.content))
        self.assertIn('dom2.supervisr.beryju.org', str(res.content))
