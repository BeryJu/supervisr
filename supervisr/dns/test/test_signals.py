"""Supervisr DNS Signal Test"""
from datetime import datetime

from django.test import TestCase

from supervisr.core.models import (Domain, User, UserAcquirableRelationship,
                                   get_system_user)
from supervisr.core.test.utils import internal_provider
from supervisr.dns.models import Record, Resource, ResourceSet, Zone
from supervisr.dns.utils import record_to_rdata


class TestSignals(TestCase):
    """Supervisr DNS Signal Test"""

    provider = None
    user = None
    credentials = None

    def setUp(self):
        self.user = User.objects.get(pk=get_system_user())
        self.provider, self.credentials = internal_provider(self.user)

    def create_single_record(self, **kwargs) -> Record:
        """Create record, resource and resourceset"""
        record_zone = kwargs.pop('record_zone')
        resource = Resource.objects.create(**kwargs)
        resource_set = ResourceSet.objects.create(
            name='test'
        )
        resource_set.resource.add(resource)
        record = Record.objects.create(
            name='test',
            record_zone=record_zone,
            resource_set=resource_set
        )
        return record

    def test_signal_soa_update(self):
        """Test automated SOA update"""
        t_domain = Domain.objects.by(self.user).create(
            domain_name='test.beryju.org',
            provider_instance=self.provider)
        t_zone = Zone(
            domain=t_domain)
        t_soa = Resource.objects.create(
            name='test SOA',
            type='SOA',
            content='ns1.s.beryju.org. support.beryju.org. 2017110401 1800 180 2419200 86400')
        t_zone.soa = t_soa
        t_zone.by(self.user).save()
        UserAcquirableRelationship.objects.create(
            model=t_zone,
            user=self.user)
        self.assertEqual(record_to_rdata(t_zone.soa, t_zone).serial, 2017110401)
        t_record_a = self.create_single_record(
            record_zone=t_zone,
            type='A',
            content='127.0.0.1')
        now = datetime.now()
        correct_serial_a = int("%04d%02d%02d01" % (now.year, now.month, now.day))
        correct_serial_b = int("%04d%02d%02d02" % (now.year, now.month, now.day))
        self.assertEqual(record_to_rdata(t_zone.soa, t_zone).serial, correct_serial_a)
        t_record_a.content = '127.0.0.2'
        t_record_a.save()
        self.assertEqual(record_to_rdata(t_zone.soa, t_zone).serial, correct_serial_b)
        t_soa.content = 'ns1.s.beryju.org. support.beryju.org. ' \
            '2aa017110401 1800 180 2419200 86400'
        t_soa.save()
        self.assertIn('2aa017110401', t_zone.soa.content)
