"""Supervisr DNS Models"""
from typing import Generator
from uuid import uuid4

from django.db import models

from supervisr.core.models import (Domain, ProviderAcquirable,
                                   ProviderTriggerMixin, UserAcquirable)

# imported from powerdns
RECORD_TYPES = (
    ('A', 'A'),
    ('AAAA', 'AAAA'),
    ('AFSDB', 'AFSDB'),
    ('APL', 'APL'),
    ('CAA', 'CAA'),
    ('CDNSKEY', 'CDNSKEY'),
    ('CDS', 'CDS'),
    ('CERT', 'CERT'),
    ('CNAME', 'CNAME'),
    ('DHCID', 'DHCID'),
    ('DLV', 'DLV'),
    ('DNAME', 'DNAME'),
    ('DNSKEY', 'DNSKEY'),
    ('DS', 'DS'),
    ('HIP', 'HIP'),
    ('IPSECKEY', 'IPSECKEY'),
    ('KEY', 'KEY'),
    ('KX', 'KX'),
    ('LOC', 'LOC'),
    ('MX', 'MX'),
    ('NAPTR', 'NAPTR'),
    ('NS', 'NS'),
    ('NSEC', 'NSEC'),
    ('NSEC3', 'NSEC3'),
    ('NSEC3PARAM', 'NSEC3PARAM'),
    ('OPENPGPKEY', 'OPENPGPKEY'),
    ('PTR', 'PTR'),
    ('RRSIG', 'RRSIG'),
    ('RP', 'RP'),
    ('SIG', 'SIG'),
    ('SRV', 'SRV'),
    ('SSHFP', 'SSHFP'),
    ('TA', 'TA'),
    ('TKEY', 'TKEY'),
    ('TLSA', 'TLSA'),
    ('TSIG', 'TSIG'),
    ('TXT', 'TXT'),
    ('URI', 'URI'),
)


class Zone(ProviderAcquirable, UserAcquirable):
    """DNS Zone"""

    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    soa_mname = models.TextField()
    soa_rname = models.TextField()
    soa_serial = models.IntegerField()
    soa_refresh = models.IntegerField(default=86400)
    soa_retry = models.IntegerField(default=7200)
    soa_expire = models.IntegerField(default=3600000)
    soa_ttl = models.IntegerField(default=172800)

    def __str__(self):
        return "Zone %s" % self.domain.domain_name


class Record(ProviderTriggerMixin, UserAcquirable):
    """DNS Record"""

    name = models.TextField()
    record_zone = models.ForeignKey('Zone', on_delete=models.CASCADE)
    resource_set = models.ForeignKey('ResourceSet', on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid4)

    @property
    def provider_instances(self) -> Generator['ProviderInstance', None, None]:
        """Return all provider instances that should be triggered"""
        return self.record_zone.provider_instances

    @property
    def fqdn(self):
        """Get full FQDN with zone"""
        if self.name == '@':
            return self.record_zone.domain.domain_name
        return "%s.%s" % (self.name, self.record_zone.domain.domain_name)

    def __str__(self):
        return "Record %s" % self.name


class Resource(ProviderTriggerMixin, UserAcquirable):
    """Record Resource"""

    name = models.TextField()
    type = models.CharField(max_length=10, choices=RECORD_TYPES)
    content = models.TextField()
    ttl = models.IntegerField(default=3600)
    priority = models.IntegerField(default=0)
    enabled = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid4)

    @property
    def provider_instances(self) -> Generator['ProviderInstance', None, None]:
        """Return all provider instances that should be triggered"""
        for resource_set in self.resourceset_set.all():
            for record in resource_set.record_set.all():
                for provider in record.record_zone.provider_instances:
                    yield provider

    def __str__(self):
        return "Resource %s %s" % (self.type, self.content)


class ResourceSet(ProviderTriggerMixin, UserAcquirable):
    """Connect Record to Resource"""

    uuid = models.UUIDField(default=uuid4)
    name = models.TextField()
    resource = models.ManyToManyField('Resource', blank=True)

    @property
    def provider_instances(self) -> Generator['ProviderInstance', None, None]:
        """Return all provider instances that should be triggered"""
        print('this is being called too early probably')
        for record in self.record_set.all():
            for provider in record.record_zone.provider_instances:
                yield provider

    def __str__(self):
        return "ResourceSet %s" % self.name
