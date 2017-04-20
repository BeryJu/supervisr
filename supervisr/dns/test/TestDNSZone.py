"""
Supervisr DNS DNSZone Test
"""

from django.test import TestCase

from supervisr.core.models import Domain

from ..models import DNSZone


class TestDNSZone(TestCase):
    """
    Supervisr DNS DNSZone Test
    """

    def setUp(self):
        pass

    def test_dnszone_get_set(self):
        """
        Test DNSZone's domain setter and getter
        """
        domain = Domain.objects.create(
            name='beryjuorgtesting.xyz',
            slug='domain-beryjuorgtestingxyz',
            invite_only=True,
            price=0)
        dns_domain = DNSZone.objects.create(
            domain=domain,
            price=0)
        self.assertEqual(dns_domain.domain, domain)
        dns_domain.domain = domain
        dns_domain.save()
        self.assertEqual(dns_domain.domain, domain)
