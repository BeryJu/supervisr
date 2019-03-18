"""supervisr dns dyndns tests"""

from django.contrib.auth.models import UserAcquirableRelationship

from supervisr.core.utils.tests import TestCase, test_request
from supervisr.dns.api.v1.record import dyndns_update
from supervisr.dns.models import DataRecord


class TestDynDNS(TestCase):
    """Test dyndns_update"""

    def test_dyndns_update(self):
        """test dyndns_update"""
        record = DataRecord.objects.create(
            name='test',
            content='1.2.3.4',
            type='A')
        response = test_request(dyndns_update, user=self.system_user, url_kwargs={
            'record_uuid': record.uuid
        })
        self.assertEqual(response.content.decode('utf-8'), 'bad auth')
        UserAcquirableRelationship.objects.create(
            user=self.system_user,
            model=record)
        response = test_request(dyndns_update, user=self.system_user, url_kwargs={
            'record_uuid': record.uuid
        })
        self.assertEqual(response.content.decode('utf-8'), 'good')
