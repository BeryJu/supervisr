"""Supervisr DNS Signal Test"""
from datetime import datetime

from supervisr.core.models import Domain, UserAcquirableRelationship
from supervisr.core.utils.tests import TestCase
from supervisr.dns.models import DataRecord, Zone


class TestSignals(TestCase):
    """Supervisr DNS Signal Test"""

    def test_signal_soa_update(self):
        """Test automated SOA update"""
        domain = Domain.objects.create(
            domain_name='test.beryju.org',
            provider_instance=self.provider)
        zone = Zone.objects.create(
            domain=domain,
            soa_mname='test',
            soa_rname='test',
            soa_serial=2017110401)
        UserAcquirableRelationship.objects.create(
            model=zone,
            user=self.system_user)
        self.assertEqual(zone.soa_serial, 2017110401)
        record = DataRecord.objects.create(
            name='test',
            type='A',
            content='127.0.0.1')
        now = datetime.now()
        self.assertEqual(zone.soa_serial, 2017110401)
        zone.records.add(record)
        record.content = '127.0.0.2'
        record.save()
        correct_serial_a = int("%04d%02d%02d01" % (now.year, now.month, now.day))
        zone.refresh_from_db()
        self.assertEqual(zone.soa_serial, correct_serial_a)
