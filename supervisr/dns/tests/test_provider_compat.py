"""supervisr dns provider compat tests"""

from unittest.mock import patch

from supervisr.core.models import Domain, ProviderAcquirableRelationship
from supervisr.core.providers.objects import ProviderObjectTranslator
from supervisr.core.utils.constants import TEST_DOMAIN
from supervisr.core.utils.tests import TestCase
from supervisr.dns.models import DataRecord, SetRecord, Zone
from supervisr.dns.providers.compat import (CompatDNSProvider, CompatDNSRecord,
                                            CompatDNSTranslator)
from supervisr.dns.utils import date_to_soa


class TestProviderCompat(TestCase):
    """Test DNS Provider Compatibility layer"""

    def setUp(self):
        super().setUp()
        self.domain, _created = Domain.objects.get_or_create(
            domain_name=TEST_DOMAIN,
            provider_instance=self.provider)
        self.zone = Zone.objects.create(
            domain=self.domain,
            soa_mname='ns1.s.beryju.org',
            soa_rname='test.beryju.org.',
            soa_serial=date_to_soa())
        ProviderAcquirableRelationship.objects.create(
            provider_instance=self.provider,
            model=self.zone)
        self.data_record_a = DataRecord.objects.create(
            name='test-a',
            type='A',
            content='1.2.3.4')
        self.data_record_b = DataRecord.objects.create(
            name='test-b',
            type='A',
            content='1.2.3.5')
        self.set_record = SetRecord.objects.create(
            name='@')
        self.set_record.records.add(self.data_record_b)
        self.zone.records.add(self.data_record_a)
        self.zone.records.add(self.set_record)

    def test_compat_record(self):
        """Test CompatDNSRecord"""
        translator = CompatDNSTranslator(None)
        compat_records = translator.build_compat_records(self.data_record_a)
        self.assertEqual(len(compat_records), 1)
        self.assertEqual(compat_records[0].name, 'test-a.supervisrtest.beryju.org')
        self.assertEqual(compat_records[0].domain, str(self.zone))

    def test_provider(self):
        """Test CompatDNSProvider"""
        provider = CompatDNSProvider(None)
        self.assertEqual(provider.get_translator(DataRecord), CompatDNSTranslator)
        self.assertEqual(provider.get_translator(CompatDNSRecord), None)

    @patch('supervisr.dns.providers.compat.CompatDNSProvider.get_translator')
    def test_translator(self, get_translator):
        """Test CompatDNSTranslator"""
        class TestTranslator(ProviderObjectTranslator):
            """Test Provider Translator"""

            def to_external(self, internal):
                yield internal
        self.set_record.records.add(self.data_record_a)
        get_translator.return_value = TestTranslator
        provider = CompatDNSProvider(None)
        translator = CompatDNSTranslator(provider)
        compat_records = list(translator.to_external(self.set_record))
        self.assertEqual(len(compat_records), 2)
        self.assertEqual(compat_records[0].name, TEST_DOMAIN)
        self.assertEqual(compat_records[1].name, TEST_DOMAIN)
