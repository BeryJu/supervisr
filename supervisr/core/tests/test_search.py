"""Supervisr Core SearchView Test"""

from supervisr.core.models import Domain
from supervisr.core.tests.utils import TestCase, internal_provider, test_request
from supervisr.core.views import search


class TestSearchView(TestCase):
    """Supervisr Core SearchView Test"""

    def test_search_404(self):
        """Test Search without query"""
        res = test_request(search.search, user=self.system_user)
        self.assertEqual(res.status_code, 404)

    def test_search_empty(self):
        """Test Search with empty results"""
        res = test_request(search.search, user=self.system_user, req_kwargs={'q': ''})
        self.assertEqual(res.status_code, 200)

    def test_search_domain(self):
        """Test search with 2 domains as result"""
        prov, _creds = internal_provider(self.system_user)
        Domain.objects.create(provider_instance=prov,
                              domain_name='dom1.supervisr.beryju.org')
        Domain.objects.create(provider_instance=prov,
                              domain_name='dom2.supervisr.beryju.org')
        res = test_request(search.search, user=self.system_user, req_kwargs={
            'q': 'supervisr.beryju.org'
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn('dom1.supervisr.beryju.org', str(res.content))
        self.assertIn('dom2.supervisr.beryju.org', str(res.content))
