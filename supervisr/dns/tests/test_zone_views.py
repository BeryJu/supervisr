"""Supervisr DNS View Test"""

from supervisr.core.models import (Domain, ProviderAcquirableRelationship,
                                   UserAcquirableRelationship)
from supervisr.core.utils.constants import TEST_DOMAIN
from supervisr.core.utils.tests import (TestCase, internal_provider,
                                        test_request)
from supervisr.dns.models import Zone
from supervisr.dns.utils import date_to_soa
from supervisr.dns.views.zones import (ZoneDeleteView, ZoneIndexView,
                                       ZoneNewView, ZoneUpdateView)


class TestZoneViews(TestCase):
    """Supervisr DNS View Test"""

    def setUp(self):
        super().setUp()
        self.provider, self.credentials = internal_provider(self.system_user)
        self.domain = Domain.objects.create(domain_name=TEST_DOMAIN,
                                            provider_instance=self.provider)
        self.zone = Zone.objects.create(domain=self.domain,
                                        soa_mname=TEST_DOMAIN,
                                        soa_rname=TEST_DOMAIN,
                                        soa_serial=date_to_soa())
        ProviderAcquirableRelationship.objects.create(
            model=self.zone, provider_instance=self.provider)
        UserAcquirableRelationship.objects.create(
            model=self.zone, user=self.system_user)

    def test_zone_index(self):
        """Test zone_index view"""
        self.assertEqual(test_request(ZoneIndexView.as_view(),
                                      user=self.system_user).status_code, 200)

    def test_zone_new(self):
        """Test ZoneNewView"""
        self.assertEqual(test_request(ZoneNewView.as_view(),
                                      user=self.system_user).status_code, 200)

    def test_zone_update(self):
        """Test ZoneUpdateView"""
        self.assertEqual(test_request(ZoneUpdateView.as_view(),
                                      method='POST',
                                      url_kwargs={'uuid': self.zone.uuid},
                                      user=self.system_user).status_code, 200)

    def test_zone_delete(self):
        """Test ZoneDeleteView"""
        self.assertEqual(test_request(ZoneDeleteView.as_view(),
                                      url_kwargs={'uuid': self.zone.uuid},
                                      user=self.system_user).status_code, 200)
        self.assertEqual(test_request(ZoneDeleteView.as_view(),
                                      method='POST',
                                      req_kwargs={'confirmdelete': True},
                                      url_kwargs={'uuid': self.zone.uuid},
                                      user=self.system_user).status_code, 302)
