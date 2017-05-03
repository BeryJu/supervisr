"""
Supervisr Web Model Test
"""

from django.contrib.auth.models import User
from django.test import TestCase

from supervisr.core.models import Domain, get_system_user

from ..models import WebDomain


class TestModels(TestCase):
    """
    Supervisr Web Model Test
    """

    def setUp(self):
        pass

    def test_maildomain_get_set(self):
        """
        Test Web ModelDomain's getter and setter
        """
        domain = Domain.objects.create(
            name='beryjuorgtesting.xyz',
            invite_only=True,
            price=0)
        web_domain = WebDomain.objects.create(
            domain_web=domain,
            profile=User.objects.get(pk=get_system_user()).userprofile)
        self.assertEqual(web_domain.domain, domain)
        web_domain.domain = domain
        web_domain.save()
        self.assertEqual(web_domain.domain, domain)
