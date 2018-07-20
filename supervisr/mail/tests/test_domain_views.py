"""Supervisr Mail DomainView Test"""

from supervisr.core.models import (BaseCredential, Domain,
                                   ProviderAcquirableRelationship,
                                   ProviderInstance,
                                   UserAcquirableRelationship)
from supervisr.core.tests.utils import TestCase, test_request
from supervisr.mail.models import MailDomain
from supervisr.mail.views import domains


class TestDomainViews(TestCase):
    """Supervisr Mail DomainView Test"""

    def setUp(self):
        super(TestDomainViews, self).setUp()
        _domain = 'supervisr-unittest.beryju.org'
        self.provider_credentials = BaseCredential.objects.create(
            owner=self.system_user, name='test-creds')
        self.provider = ProviderInstance.objects.create(
            provider_path='supervisr.core.providers.base.BaseProvider',
            credentials=self.provider_credentials)
        self.ddomain = Domain.objects.create(domain_name=_domain,
                                             provider_instance=self.provider)
        UserAcquirableRelationship.objects.create(user=self.system_user, model=self.ddomain)
        self.domain = MailDomain.objects.create(domain=self.ddomain)
        ProviderAcquirableRelationship.objects.create(model=self.domain,
                                                      provider_instance=self.provider)
        UserAcquirableRelationship.objects.create(user=self.system_user, model=self.domain)

    def test_domain_index(self):
        """Test Domain Index"""
        self.assertEqual(test_request(domains.MailDomainIndexView.as_view(),
                                      user=self.system_user).status_code, 200)

    def test_domain_view(self):
        """Test Index View (Anonymous)"""
        self.assertEqual(test_request(domains.MailDomainReadView.as_view(), url_kwargs={
            'domain': self.domain.domain.domain_name
        }).status_code, 302)

    def test_domain_view_auth(self):
        """Test Index View (Authenticated)"""
        self.assertEqual(
            test_request(domains.MailDomainReadView.as_view(),
                         user=self.system_user,
                         url_kwargs={'domain': self.domain.domain.domain_name}).status_code, 200)

    def test_domain_view_404(self):
        """Test Index View (non-existant)"""
        self.assertEqual(
            test_request(domains.MailDomainReadView.as_view(),
                         user=self.system_user,
                         url_kwargs={'domain': 'invalid'}).status_code, 404)
