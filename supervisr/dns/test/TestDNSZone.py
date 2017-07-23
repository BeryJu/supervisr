"""
Supervisr DNS DNSDomain Test
"""

from django.test import TestCase

from supervisr.core.models import Domain
from supervisr.dns.models import DNSDomain


class TestDNSDomain(TestCase):
    """
    Supervisr DNS DNSDomain Test
    """

    def setUp(self):
        pass

    def test_dnsdomain_get_set(self):
        """
        Test DNSDomain's domain setter and getter
        """
        domain = Domain.objects.create(
            name='beryjuorgtesting.xyz',
            slug='domain-beryjuorgtestingxyz',
            invite_only=True,
            price=0)
        dns_domain = DNSDomain.objects.create(
            domain=domain,
            price=0)
        self.assertEqual(dns_domain.domain, domain)
        dns_domain.domain = domain
        dns_domain.save()
        self.assertEqual(dns_domain.domain, domain)
