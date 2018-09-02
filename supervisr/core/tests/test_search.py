"""Supervisr Core SearchView Test"""

from supervisr.core.models import Domain, UserAcquirableRelationship
from supervisr.core.tests.utils import TestCase, test_request
from supervisr.core.views.search import (DefaultSearchHandler, SearchQuery,
                                         SearchView)


class TestSearchView(TestCase):
    """Supervisr Core SearchView Test"""

    def setUp(self):
        super().setUp()
        dom1, _ = Domain.objects.get_or_create(provider_instance=self.provider,
                                               domain_name='dom1.supervisr.beryju.org')
        dom2, _ = Domain.objects.get_or_create(provider_instance=self.provider,
                                               domain_name='dom2.supervisr.beryju.org')
        UserAcquirableRelationship.objects.get_or_create(user=self.system_user,
                                                         model=dom1)
        UserAcquirableRelationship.objects.get_or_create(user=self.system_user,
                                                         model=dom2)

    def test_search_404(self):
        """Test Search without query"""
        res = test_request(SearchView.as_view(), user=self.system_user)
        self.assertEqual(res.status_code, 404)

    def test_search_view_empty(self):
        """Test Search with empty results"""
        res = test_request(SearchView.as_view(), user=self.system_user, req_kwargs={'q': ''})
        self.assertEqual(res.status_code, 404)

    def test_search_domain(self):
        """Test search with 2 domains as result"""
        response = test_request(SearchView.as_view(), user=self.system_user, req_kwargs={
            'q': 'supervisr.beryju.org'
        })
        response.render()
        self.assertEqual(response.status_code, 200)
        self.assertInHTML('dom1.supervisr.beryju.org', response.content.decode('utf-8'))
        self.assertInHTML('dom2.supervisr.beryju.org', response.content.decode('utf-8'))

    def test_search_filter(self):
        """Test search with 0 domains as result, with filter"""
        response = test_request(SearchView.as_view(), user=self.system_user, req_kwargs={
            'q': 'supervisr.beryju.org',
            'filter_app': 'supervisr_core',
            'filter_model': 'Domain',
        })
        response.render()
        self.assertEqual(response.status_code, 200)
        self.assertInHTML('dom1.supervisr.beryju.org', response.content.decode('utf-8'))
        self.assertInHTML('dom2.supervisr.beryju.org', response.content.decode('utf-8'))
        self.assertInHTML('Search everything...', response.content.decode('utf-8'))

    def test_search_view(self):
        """Test Search view logic"""
        # Search Handler requires a request for user info so mock one
        request = test_request(SearchView.as_view(), user=self.system_user, just_request=True)
        view_instance = SearchView()
        view_instance.request = request
        query = SearchQuery()
        query.query = 'supervisr.beryju.org'
        results = view_instance.search(query)
        self.assertIn('Supervisr Core', results)
        self.assertIn(Domain, results['Supervisr Core'])
        self.assertEqual(len(results['Supervisr Core'][Domain]), 3)
        self.assertEqual(results['Supervisr Core'][Domain][0].label, 'dom1.supervisr.beryju.org')

    def test_default_search_handler(self):
        """Test default search algorithm"""
        # Search Handler requires a request for user info so mock one
        request = test_request(SearchView.as_view(), user=self.system_user, just_request=True)
        handler = DefaultSearchHandler(model=Domain,
                                       fields=['domain_name', 'description'],
                                       label_field='domain_name', icon='world',
                                       view_name='domain-index')
        query = SearchQuery()
        query.query = 'supervisr.beryju.org'
        results = handler.search(query, request)
        self.assertEqual(len(results[Domain]), 3)
        self.assertEqual(results[Domain][0].label, 'dom1.supervisr.beryju.org')

    def test_search_handler_empty(self):
        """Test default search algorithm"""
        # Search Handler requires a request for user info so mock one
        request = test_request(SearchView.as_view(), user=self.system_user, just_request=True)
        handler = DefaultSearchHandler(model=Domain,
                                       fields=['domain_name', 'description'],
                                       label_field='domain_name', icon='world',
                                       view_name='domain-index')
        query = SearchQuery()
        query.query = 'sssupervisr.beryju.org'
        results = handler.search(query, request)
        self.assertEqual(len(results), 0)

    def test_search_url_kwargs(self):
        """Test DefaultSearchHandler's view_kwarg_name"""
        # Search Handler requires a request for user info so mock one
        request = test_request(SearchView.as_view(), user=self.system_user, just_request=True)
        handler = DefaultSearchHandler(model=Domain,
                                       fields=['domain_name', 'description'],
                                       label_field='domain_name', icon='world',
                                       view_name='domain-edit',
                                       view_kwarg_name='domain')
        query = SearchQuery()
        query.query = 'supervisr.beryju.org'
        results = handler.search(query, request)
        self.assertEqual(len(results[Domain]), 3)
        self.assertEqual(results[Domain][0].label, 'dom1.supervisr.beryju.org')
