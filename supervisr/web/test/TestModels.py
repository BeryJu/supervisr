"""
Supervisr Web Model Test
"""

from django.test import TestCase

from supervisr.core.models import (BaseCredential, Domain, ProviderInstance,
                                   User, get_system_user)
from supervisr.web.models import WebDomain


class TestModels(TestCase):
    """
    Supervisr Web Model Test
    """

    def setUp(self):
        self.user = User.objects.get(pk=get_system_user())
        self.provider_credentials = BaseCredential.objects.create(
            owner=self.user, name='test-creds')
        self.provider = ProviderInstance.objects.create(
            provider_path='supervisr.core.providers.base.BaseProvider',
            credentials=self.provider_credentials)

    def test_maildomain_get_set(self):
        """
        Test Web ModelDomain's getter and setter
        """
        domain = Domain.objects.create(
            name='beryjuorgtesting.xyz',
            provider=self.provider)
        web_domain = WebDomain.objects.create(
            domain_web=domain)
        self.assertEqual(web_domain.domain, domain)
        web_domain.domain = domain
        web_domain.save()
        self.assertEqual(web_domain.domain, domain)
