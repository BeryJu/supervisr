"""
Supervisr Mail DomainView Test
"""

import os

from django.contrib.auth.models import User
from django.test import TestCase

from supervisr.core.models import (BaseCredential, Domain, ProviderInstance,
                                   UserProductRelationship, get_system_user)
from supervisr.core.test.utils import test_request
from supervisr.mail.models import MailDomain
from supervisr.mail.views import domain


class TestDomainViews(TestCase):
    """
    Supervisr Mail DomainView Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        _domain = 'supervisr-unittest.beryju.org'
        self.user = User.objects.get(pk=get_system_user())
        self.provider_credentials = BaseCredential.objects.create(
            owner=self.user, name='test-creds')
        self.provider = ProviderInstance.objects.create(
            provider_path='supervisr.core.providers.base.BaseProvider',
            credentials=self.provider_credentials)
        self.ddomain = Domain.objects.create(domain=_domain, is_sub=True, provider=self.provider)
        UserProductRelationship.objects.create(user=self.user, product=self.ddomain)
        self.domain = MailDomain.objects.create(domain=self.ddomain, provider=self.provider)
        UserProductRelationship.objects.create(user=self.user, product=self.domain)

    def test_domain_view(self):
        """
        Test Index View (Anonymous)
        """
        self.assertEqual(test_request(domain.view, url_kwargs={
            'domain': self.domain.domain.domain
            }).status_code, 302)

    def test_domain_view_auth(self):
        """
        Test Index View (Authenticated)
        """
        self.assertEqual(test_request(domain.view, user=get_system_user(), url_kwargs={
            'domain': self.domain.domain.domain
            }).status_code, 200)

    def test_domain_view_404(self):
        """
        Test Index View (non-existant)
        """
        self.assertEqual(test_request(domain.view, user=get_system_user(), url_kwargs={
            'domain': 'invalid'
            }).status_code, 404)
