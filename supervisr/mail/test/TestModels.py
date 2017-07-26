"""
Supervisr Mail Test
"""

from django.contrib.auth.models import User
from django.test import TestCase

from supervisr.core.models import (BaseCredential, Domain, ProviderInstance,
                                   get_system_user)
from supervisr.mail.models import MailAccount, MailDomain


class TestModels(TestCase):
    """
    Supervisr Mail Test
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
        Test MailDomain's getter and setter
        """
        domain = Domain.objects.create(
            name='supervisr-unittest.beryju.org',
            invite_only=True,
            price=0)
        mx_domain = MailDomain.objects.create(domain=domain, provider=self.provider)
        self.assertEqual(mx_domain.domain, domain)
        mx_domain.domain = domain
        mx_domain.save()
        self.assertFalse(mx_domain.has_catchall)
        self.assertEqual(mx_domain.domain, domain)

    def test_mailaccount_get_set(self):
        """
        Test MailAccount's getter and setter
        """
        domain = Domain.objects.create(
            name='supervisr-unittest.beryju.org',
            invite_only=True,
            price=0)
        mx_domain = MailDomain.objects.create(domain=domain, provider=self.provider)
        self.assertEqual(mx_domain.domain, domain)
        mx_account = MailAccount.objects.create(
            address='info',
            domain=mx_domain,
            price=0)
        self.assertEqual(mx_account.search_title(), mx_account.email)
        self.assertEqual(mx_account.domain, mx_domain)

    def test_mailaccount_password(self):
        """
        Test MailAccount's set_password
        """
        domain = Domain.objects.create(
            name='supervisr-unittest.beryju.org',
            invite_only=True,
            price=0)
        mx_domain = MailDomain.objects.create(domain=domain, provider=self.provider)
        self.assertEqual(mx_domain.domain, domain)
        mx_account = MailAccount.objects.create(
            address='info',
            domain=mx_domain,
            price=0)
        self.assertEqual(mx_account.domain, mx_domain)
        usr = User.objects.get(pk=get_system_user())
        mx_account.set_password(usr, 'test', salt='testtest')
        self.assertEqual(mx_account.password, ('$6$rounds=656000$testtest$CaN82QPQ6BrS4VJ7R8Nuxoow'
                                               'ctnCSXRhXnFE4je8MGWN7bIvPsU0yVZgG0ZrPAw44DzIi/NhDng'
                                               'vVkJ7w6B3M0'))
