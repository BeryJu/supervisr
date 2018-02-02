"""
Supervisr DNS Signal Test
"""
from datetime import datetime

from django.test import TestCase

from supervisr.core.models import Domain, User, get_system_user
from supervisr.core.test.utils import internal_provider
from supervisr.dns.models import Record, Zone
from supervisr.dns.utils import rec_to_rd


class TestSignals(TestCase):
    """
    Supervisr DNS Signal Test
    """

    provider = None
    credentials = None

    def setUp(self):
        user = User.objects.get(pk=get_system_user())
        self.provider, self.credentials = internal_provider(user)

    def test_signal_soa_update(self):
        """
        Test Signal's domain setter and getter
        """
        t_domain = Domain.objects.create(
            domain='test.beryju.org',
            provider=self.provider)
        t_zone = Zone.objects.create(
            domain=t_domain,
            provider=self.provider)
        t_record_soa = Record.objects.create(
            domain=t_zone,
            type='SOA',
            content='ns1.s.beryju.org. support.beryju.org. 2017110401 1800 180 2419200 86400')
        self.assertEqual(rec_to_rd(t_zone.soa).serial, 2017110401)
        t_record_a = Record.objects.create(
            domain=t_zone,
            type='A',
            content='127.0.0.1')
        now = datetime.now()
        correct_serial_a = int("%04d%02d%02d01" % (now.year, now.month, now.day))
        correct_serial_b = int("%04d%02d%02d02" % (now.year, now.month, now.day))
        self.assertEqual(rec_to_rd(t_zone.soa).serial, correct_serial_a)
        t_record_a.content = '127.0.0.2'
        t_record_a.save()
        self.assertEqual(rec_to_rd(t_zone.soa).serial, correct_serial_b)
        t_record_soa.content = 'ns1.s.beryju.org. support.beryju.org. ' \
                               '2aa017110401 1800 180 2419200 86400'
        t_record_soa.save()
        self.assertIn('2aa017110401', t_zone.soa.content)
