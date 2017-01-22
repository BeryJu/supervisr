"""
Supervisr Mail Test
"""

from django.test import TestCase

from supervisr.models import Domain

from ..models import MailAccount, MailDomain


class TestMail(TestCase):
    """
    Supervisr Mail Test
    """

    def setUp(self):
        pass

    def test_maildomain_get_set(self):
        """
        Test MailDomain's getter and setter
        """
        domain = Domain.objects.create(
            name='beryjuorgtesting.xyz',
            slug='domain-beryjuorgtestingxyz',
            invite_only=True,
            price=0)
        mx_domain = MailDomain.objects.create(
            domain=domain,
            price=0)
        self.assertEqual(mx_domain.domain, domain)
        mx_domain.domain = domain
        mx_domain.save()
        self.assertEqual(mx_domain.domain, domain)

    def test_mailaccount_get_set(self):
        """
        Test MailAccount's getter and setter
        """
        domain = Domain.objects.create(
            name='beryjuorgtesting.xyz',
            slug='domain-beryjuorgtestingxyz',
            invite_only=True,
            price=0)
        mx_domain = MailDomain.objects.create(
            domain=domain,
            price=0)
        self.assertEqual(mx_domain.domain, domain)
        mx_account = MailAccount.objects.create(
            address='info',
            domain=mx_domain,
            price=0)
        self.assertEqual(mx_account.domain, mx_domain)
